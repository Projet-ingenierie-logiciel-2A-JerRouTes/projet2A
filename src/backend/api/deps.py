from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.backend.api.config import settings
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
    1) Lit le header Authorization: Bearer <token>
    2) Décode et valide le JWT
    3) Extrait les infos minimales (uid, sid, status)
    """

    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = creds.credentials

    try:
        payload = decode_jwt(
            token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
        )
    except (JWTExpiredError, JWTInvalidTokenError, JWTIssuerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    uid = payload.get("uid")
    sid = payload.get("sid")
    status_ = payload.get("status")

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

    try:
        user_service.get_user(cu.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return cu
