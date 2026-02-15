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
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserNotFoundError,
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
    # --- INTERCEPTION MODE DÉMO ---
    if settings.use_seed_data:
        return TokenPairResponse(
            access_token="demo-token-123",
            refresh_token="demo-refresh-123",
            session_id=999,
        )

    # --- LOGIQUE RÉELLE ---
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
    "/login_v2",
    response_model=TokenPairResponse,
    summary="Connexion utilisateur",
    response_description="Retourne les tokens JWT (access et refresh) et le profil utilisateur",
)
def login_v2(req: LoginRequest, request: Request) -> TokenPairResponse:
    """
    Authentifie un utilisateur et génère une session sécurisée.

    - **login**: Pseudo ou Email de l'utilisateur
    - **password**: Mot de passe en clair (sera vérifié via bcrypt ou check_password)

    Le serveur récupère automatiquement l'IP et le User-Agent pour sécuriser la session.
    """
    # --- INTERCEPTION MODE DÉMO SÉCURISÉE ---
    if settings.use_seed_data:
        from src.backend.scripts.seed_data import get_demo_data

        data = get_demo_data()

        # On cherche l'utilisateur par pseudo ou email dans le seed
        user_demo = next(
            (u for u in data["users"] if u.pseudo == req.login or u.email == req.login),
            None,
        )

        if not user_demo:
            raise HTTPException(
                status_code=404, detail="Utilisateur inconnu (Mode Démo)"
            )

        # On utilise la méthode check_password de ton objet métier User
        if not user_demo.check_password(req.password):
            raise HTTPException(
                status_code=401, detail="Mot de passe incorrect (Mode Démo)"
            )

        # On génère le token correspondant à l'ID sélectionné
        token = (
            "demo-token-admin-123" if user_demo.id_user == 1 else "demo-token-user-456"
        )

        return TokenPairResponse(
            access_token=token,
            refresh_token="demo-refresh-123",
            session_id=999,
        )
    # --- LOGIQUE RÉELLE ---
    auth_service = _auth_service()

    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        # Appel au service qui gère maintenant les modes Démo et Réel
        tokens = auth_service.login(
            login=req.login,
            password=req.password,
            ip=ip,
            user_agent=user_agent,
        )

    except UserNotFoundError as exc:
        # Capture l'utilisateur inconnu -> Renvoie 404 pour le Frontend
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except InvalidPasswordError as exc:
        # Capture le mauvais mot de passe -> Renvoie 401 pour le Frontend
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except InvalidCredentialsError as exc:
        # Capture les erreurs d'identifiants génériques (ex: Mode Démo)
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except Exception as exc:
        # Sécurité ultime pour éviter l'instabilité thermique du serveur
        raise HTTPException(
            status_code=500, detail="Erreur interne du serveur"
        ) from exc

    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        session_id=tokens.session_id,
    )


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Connexion utilisateur",
    response_description="Retourne les tokens JWT et le profil utilisateur",
)
def login(
    req: LoginRequest,
    request: Request,
    admin: bool = False,  # Paramètre optionnel (Query Parameter)
) -> TokenPairResponse:
    """
    Authentifie un utilisateur et génère une session sécurisée.

    - **login**: Pseudo ou Email de l'utilisateur.
    - **password**: Mot de passe en clair.
    - **admin**: Si True, restreint la connexion aux comptes ayant le statut 'admin'.
    """

    # --- 1. INTERCEPTION MODE DÉMO (Simulation avec Seed Data) ---
    if settings.use_seed_data:
        from src.backend.scripts.seed_data import get_demo_data

        data = get_demo_data()

        # Recherche de l'utilisateur dans la liste de démo
        user_demo = next(
            (u for u in data["users"] if u.pseudo == req.login or u.email == req.login),
            None,
        )

        if not user_demo:
            raise HTTPException(
                status_code=404, detail="Utilisateur inconnu (Mode Démo)"
            )

        # VÉRIFICATION DU RÔLE ADMIN
        if admin and user_demo.status != "admin":
            raise HTTPException(
                status_code=403,
                detail="Accès refusé : Droits administrateur requis (Mode Démo).",
            )

        # Vérification du mot de passe (comparaison en clair pour le seed)
        if not user_demo.check_password(req.password):
            raise HTTPException(
                status_code=401, detail="Mot de passe incorrect (Mode Démo)"
            )

        # On simule un token selon l'ID pour la cohérence
        token = (
            "demo-token-admin-123" if user_demo.id_user == 1 else "demo-token-user-456"
        )

        return TokenPairResponse(
            access_token=token,
            refresh_token="demo-refresh-123",
            session_id=999,
        )

    # --- 2. LOGIQUE RÉELLE (Production / Base de données) ---
    auth_service = _auth_service()
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        # Authentification via le service (vérification bcrypt incluse)
        auth_info = auth_service.authenticate(login=req.login, password=req.password)
        user = auth_info.user

        # VÉRIFICATION DU RÔLE ADMIN RÉEL
        if admin and user.status != "admin":
            raise HTTPException(
                status_code=403, detail="Accès réservé au personnel autorisé."
            )

        # Création de la session et des tokens JWT
        tokens = auth_service.create_session(
            user_id=user.id_user, ip=ip, user_agent=user_agent
        )

        return TokenPairResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            session_id=tokens.session_id,
        )

    except (UserNotFoundError, InvalidCredentialsError):
        # Pour la sécurité, on évite de préciser si c'est le login ou le mdp qui est faux
        raise HTTPException(status_code=401, detail="Identifiants invalides") from None

    except Exception as exc:
        # En cas de crash inattendu
        raise HTTPException(
            status_code=500, detail="Une erreur interne est survenue sur le serveur"
        ) from exc


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
