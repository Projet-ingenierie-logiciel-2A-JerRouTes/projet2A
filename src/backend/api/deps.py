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


def get_current_user(
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
        # On récupère l'ID choisi dynamiquement sur le dashboard
        uid = getattr(settings, "demo_user_id", 1)

        # On adapte le statut pour que les tests de droits fonctionnent (Admin vs Generic)
        role = "admin" if uid == 1 else "generic"

        # On retourne l'utilisateur simulé avec son vrai ID (1 ou 2)
        return CurrentUser(user_id=uid, session_id=1, status=role)

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


def get_current_user_checked_exists(
    cu: CurrentUser = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(get_user_service),  # noqa: B008
) -> CurrentUser:
    """
    Variante plus stricte :
    - JWT valide
    - ET utilisateur toujours présent en BDD
    """
    # --- SÉCURITÉ : BYPASS RÉSERVÉ AU MODE DÉMO ---
    # La condition settings.use_seed_data est le verrou principal.
    # Si on est en mode démo, on valide directement l'utilisateur fictif
    if settings.use_seed_data:
        return cu

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
