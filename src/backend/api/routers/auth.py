from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.config import settings
from api.deps import (
    CurrentUser,
    get_current_user_checked_exists,
    get_current_user_optional,
)
from api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
)
from exceptions import (
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserAlreadyExistsError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from services.auth_service import (
    AuthService,
)
from services.user_service import (
    # InvalidPasswordError,
    # UserNotFoundError,
    UserService,
)


# ---------------------------------------------------------------------
# Gestionnaire d'erreurs centralisé
# ---------------------------------------------------------------------


def _map_service_errors(exc: Exception) -> HTTPException:
    """
    Transforme les exceptions métier en exceptions HTTP avec messages personnalisés.
    """

    # ----------------------------
    # REGISTER
    # ----------------------------

    if isinstance(exc, UserAlreadyExistsError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identifiant déjà utilisé",
        )

    if isinstance(exc, UserEmailAlreadyExistsError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mail déjà utilisé",
        )

    # ----------------------------
    # LOGIN
    # ----------------------------

    if isinstance(exc, UserNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identifiant inconnu. Ce compte n'existe pas.",
        )

    if isinstance(exc, InvalidPasswordError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect. Veuillez réessayer.",
        )

    # 🔥 AJOUT IMPORTANT
    # Certains services lèvent une exception générique
    # avec le message "Identifiants invalides."
    if "Identifiants invalides" in str(exc):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )

    # ----------------------------
    # REFRESH
    # ----------------------------

    if isinstance(exc, InvalidRefreshTokenError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Problème dans le refresh",
        )

    # ----------------------------
    # Cas non géré
    # ----------------------------

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Erreur non gérée : {str(exc)}",
    )


# ---------------------------------------------------------------------
# Configuration du Routeur
# ---------------------------------------------------------------------

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_service() -> AuthService:
    """
    Centralise la config JWT (secret, issuer, TTL).
    """
    return AuthService(
        jwt_secret=settings.jwt_secret,
        jwt_issuer=settings.jwt_issuer,
        access_ttl_minutes=settings.access_ttl_minutes,
        refresh_ttl_days=settings.refresh_ttl_days,
    )


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------


@router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
    response_description="Utilisateur créé avec succès, retourne les tokens de session",
    responses={
        409: {"description": "L'identifiant (email ou pseudo) existe déjà."},
        422: {"description": "Format de données incorrects"},
        500: {"description": "Erreur interne du serveur."},
    },
)
def register(
    req: RegisterRequest,
    request: Request,
    cu: CurrentUser | None = Depends(get_current_user_optional),  # noqa: B008
) -> TokenPairResponse:
    """
    Crée un compte utilisateur et génère immédiatement une session.

    Par défaut, le compte est créé avec le statut "user".
    Si `est_admin` est défini à true, le compte sera créé avec
    le statut "admin" (réservé aux administrateurs).

    - **username**: Pseudo unique choisi par l'utilisateur
    - **email**: Adresse email unique
    - **password**: Mot de passe (sera haché avant stockage)
    - **est_admin**: Indique si le compte doit être administrateur (false par défaut)
    """
    user_service = UserService()
    auth_service = _auth_service()

    # Par défaut : user
    status_to_create = "user"

    # Admin uniquement si est_admin=True
    if req.est_admin:
        if cu is None or not cu.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs.",
            )
        status_to_create = "admin"

    try:
        user_service.register(
            username=req.username,
            email=req.email,
            password=req.password,
            status=status_to_create,
        )

        return auth_service.login(
            login=req.email,
            password=req.password,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as exc:
        raise _map_service_errors(exc) from exc


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Connexion utilisateur",
    response_description="Retourne les tokens JWT (access et refresh) et le profil utilisateur",
    responses={
        404: {"description": "L'identifiant (email ou pseudo) n'existe pas."},
        401: {"description": "Le mot de passe est incorrect."},
        422: {"description": "Format de données incorrects"},
        500: {"description": "Erreur interne du serveur."},
    },
)
def login(req: LoginRequest, request: Request) -> TokenPairResponse:
    """
    Authentifie un utilisateur et génère une session sécurisée.

    - **login**: Pseudo ou Email de l'utilisateur
    - **password**: Mot de passe en clair

    Distingue les erreurs de **Username** (404) et de **Mot de passe** (401).
    """
    auth_service = _auth_service()
    try:
        # On tente la connexion
        return auth_service.login(
            login=req.login,
            password=req.password,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as exc:
        # On récupère l'objet HTTPException créé par le mapper
        error_to_raise = _map_service_errors(exc)
        # On LEVE l'erreur
        raise error_to_raise from exc


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Renouvellement du token d'accès",
    response_description="Nouveau couple de tokens (Access & Refresh)",
    responses={
        401: {"description": "Problème dans le refresh"},
        422: {"description": "Format de données incorrects"},
        500: {"description": "Erreur interne du serveur."},
    },
)
def refresh(req: RefreshRequest) -> TokenPairResponse:
    """
    Utilise un Refresh Token valide pour obtenir un nouveau Access Token.
    """
    auth_service = _auth_service()
    try:
        return auth_service.refresh(refresh_token=req.refresh_token)
    except Exception as exc:
        raise _map_service_errors(exc) from exc


@router.get("/admin-status", response_model=bool)
def admin_status(
    cu: CurrentUser = Depends(get_current_user_checked_exists),
):
    """Retourne True si l'utilisateur connecté est admin."""
    return cu.is_admin()
