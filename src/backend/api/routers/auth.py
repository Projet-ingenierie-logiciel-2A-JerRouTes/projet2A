from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from src.backend.api.config import settings
from src.backend.api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
)
from src.backend.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from src.backend.services.user_service import UserAlreadyExistsError, UserService


router = APIRouter(prefix="/api/auth", tags=["Authentification"])


def _auth_service() -> AuthService:
    """
    Centralise la config JWT (secret, issuer, TTL) pour éviter
    d'avoir des valeurs en dur dans les routes.
    """
    return AuthService(
        jwt_secret=settings.jwt_secret,
        jwt_issuer=settings.jwt_issuer,
        access_ttl_minutes=settings.access_ttl_minutes,
        refresh_ttl_days=settings.refresh_ttl_days,
    )


@router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Création de compte",
    response_description="Message de confirmation et jetons d'accès (JWT)",
)
def register(req: RegisterRequest, request: Request) -> TokenPairResponse:
    """
    Enregistre un nouvel utilisateur dans la base de données.
    - Vérifie l'unicité du pseudo/email.
    - Hache le mot de passe (via bcrypt).
    - Crée une session et retourne les tokens d'accès.
    """
    user_service = UserService()
    auth_service = _auth_service()

    try:
        user_service.register(
            username=req.username,
            email=req.email,
            password=req.password,
            status="user",
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = auth_service.login(
        login=req.email,  # on log via email après inscription
        password=req.password,
        ip=ip,
        user_agent=user_agent,
    )

    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        session_id=tokens.session_id,
    )


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Connexion utilisateur",
    response_description="Retourne les tokens JWT (access et refresh) et le profil utilisateur",
)
def login(req: LoginRequest, request: Request) -> TokenPairResponse:
    """
    Authentifie un utilisateur et génère une session sécurisée.

    - **login**: Pseudo ou Email de l'utilisateur
    - **password**: Mot de passe en clair (sera vérifié via bcrypt)

    Le serveur récupère automatiquement l'IP et le User-Agent pour sécuriser la session.
    """
    auth_service = _auth_service()

    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        tokens = auth_service.login(
            login=req.login,
            password=req.password,
            ip=ip,
            user_agent=user_agent,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        session_id=tokens.session_id,
    )


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Renouveler les jetons d'accès",
    response_description="Nouvelle paire de jetons (Access et Refresh)",
)
def refresh(req: RefreshRequest) -> TokenPairResponse:
    """
    Renouvelle le jeton d'accès (Access Token) en utilisant un jeton de rafraîchissement valide.

    - **refresh_token**: Le jeton longue durée obtenu lors de la connexion initiale.

    Cette opération permet de :
    1. Vérifier si la session est toujours active en base de données.
    2. Générer un nouvel Access Token (courte durée).
    3. Optionnellement, faire tourner le Refresh Token (Refresh Token Rotation) pour plus de sécurité.
    """
    auth_service = _auth_service()
    try:
        tokens = auth_service.refresh(refresh_token=req.refresh_token)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        session_id=tokens.session_id,
    )
