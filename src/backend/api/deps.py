from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.backend.api.config import settings
from src.backend.services.stock_service import StockService
from src.backend.services.user_service import UserNotFoundError, UserService
from src.backend.utils.jwt_utils import (
    JWTExpiredError,
    JWTInvalidTokenError,
    JWTIssuerError,
    decode_jwt,
)


# Schéma "Authorization: Bearer <token>"
bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """
    Représente l'utilisateur authentifié courant,
    extrait du JWT.
    """

    user_id: int
    session_id: int
    status: str


def get_user_service() -> UserService:
    """
    Fournit une instance de UserService.
    (séparable facilement pour tests)
    """
    return UserService()


def get_current_user_v2(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008
) -> CurrentUser:
    """
    1) Vérifie la présence du token.
    2) Si mode démo + token magique : bypass immédiat.
    3) Sinon : décodage et validation stricte du JWT.
    """

    # Vérification de la présence du header Authorization
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = creds.credentials

    # --- ÉTAPE 1 : BYPASS PRIORITAIRE (MODE DÉMO) ---
    if settings.use_seed_data and token == "demo-token-123":
        # Ajout du session_id=999 pour respecter le contrat de la dataclass CurrentUser
        return CurrentUser(
            user_id=settings.demo_user_id,
            session_id=999,
            status="admin" if settings.demo_user_id == 1 else "generic",
        )

    # --- ÉTAPE 2 : LOGIQUE RÉELLE (DÉCODAGE JWT) ---
    try:
        # Si on arrive ici, le token doit être un vrai JWT
        payload = decode_jwt(
            token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
        )
    except (JWTExpiredError, JWTInvalidTokenError, JWTIssuerError, Exception) as exc:
        # On capture 'Exception' pour transformer toute erreur de format en 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # Extraction des données du payload
    uid = payload.get("uid")
    sid = payload.get("sid")
    status_ = payload.get("status")

    # --- ÉTAPE 3 : VÉRIFICATION STRICTE DU SCHÉMA ---
    if (
        not isinstance(uid, int)
        or not isinstance(sid, int)
        or not isinstance(status_, str)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    return CurrentUser(
        user_id=uid,
        session_id=sid,
        status=status_,
    )


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008
) -> CurrentUser:
    """
    1) Vérifie la présence du token.
    2) Si mode démo + token magique : bypass immédiat avec l'ID du dashboard.
    3) Sinon : décodage et validation stricte du JWT.
    """

    # Vérification de la présence du header Authorization
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )

    token = creds.credentials

    # --- ÉTAPE 1 : BYPASS PRIORITAIRE (MODE DÉMO) ---
    # On autorise les tokens générés par le dashboard (ex: demo-token-admin-123)
    if settings.use_seed_data and token.startswith("demo-token-"):
        return CurrentUser(
            user_id=settings.demo_user_id,
            session_id=999,  # Session fictive pour le mode démo
            status="admin" if settings.demo_user_id == 1 else "utilisateur",
        )

    # --- ÉTAPE 2 : LOGIQUE RÉELLE (DÉCODAGE JWT) ---
    try:
        payload = decode_jwt(
            token=token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
        )
    except JWTExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except (JWTInvalidTokenError, JWTIssuerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    # Extraction des données du payload (pour le mode BDD réelle)
    uid = payload.get("uid")
    sid = payload.get("sid")
    status_ = payload.get("status")

    # --- ÉTAPE 3 : VÉRIFICATION DU SCHÉMA DU TOKEN ---
    if (
        not isinstance(uid, int)
        or not isinstance(sid, int)
        or not isinstance(status_, str)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    return CurrentUser(
        user_id=uid,
        session_id=sid,
        status=status_,
    )


def get_current_user_checked_exists(
    cu: CurrentUser = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(get_user_service),  # noqa: B008
) -> CurrentUser:
    """
    Variante plus stricte :
    - JWT valide
    - ET utilisateur toujours présent en BDD
    """
    # --- INTERCEPTION MODE DÉMO ---
    if settings.use_seed_data:
        # On valide juste que l'ID utilisateur est bien celui configuré sur le dashboard
        return cu

    # --- LOGIQUE RÉELLE (PostgreSQL) ---

    # --- LOGIQUE RÉELLE ---
    try:
        user_service.get_user(cu.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return cu


def get_stock_service() -> StockService:
    """Fournit une instance de StockService."""
    return StockService()
