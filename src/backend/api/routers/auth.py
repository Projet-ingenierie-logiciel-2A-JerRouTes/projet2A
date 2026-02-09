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


router = APIRouter(prefix="/api/auth", tags=["auth"])


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
    "/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED
)
def register(req: RegisterRequest, request: Request) -> TokenPairResponse:
    """
    Crée l'utilisateur puis le connecte directement (retourne tokens).
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


@router.post("/login", response_model=TokenPairResponse)
def login(req: LoginRequest, request: Request) -> TokenPairResponse:
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


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(req: RefreshRequest) -> TokenPairResponse:
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
