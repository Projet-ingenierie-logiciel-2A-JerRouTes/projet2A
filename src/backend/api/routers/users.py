from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.api.config import settings
from src.backend.api.deps import CurrentUser, get_current_user_checked_exists
from src.backend.api.schemas.users import (
    ChangePasswordRequest,
    MeResponse,
    UpdateMeRequest,
    UserPublic,
)
from src.backend.services.auth_service import AuthService
from src.backend.services.user_service import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


router = APIRouter(prefix="/api/users", tags=["users"])


def _auth_service() -> AuthService:
    return AuthService(
        jwt_secret=settings.jwt_secret,
        jwt_issuer=settings.jwt_issuer,
        access_ttl_minutes=settings.access_ttl_minutes,
        refresh_ttl_days=settings.refresh_ttl_days,
    )


@router.get("/me", response_model=MeResponse)
def me(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> MeResponse:
    user_service = UserService()
    try:
        user = user_service.get_user(cu.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MeResponse(
        user=UserPublic(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            status=user.status,
        )
    )


@router.patch("/me", response_model=MeResponse)
def update_me(
    req: UpdateMeRequest,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> MeResponse:
    user_service = UserService()

    try:
        user = user_service.update_profile(
            cu.user_id,
            username=req.username,
            email=req.email,
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MeResponse(
        user=UserPublic(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            status=user.status,
        )
    )


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    req: ChangePasswordRequest,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> None:
    user_service = UserService()

    try:
        user_service.change_password(
            user_id=cu.user_id,
            old_password=req.old_password,
            new_password=req.new_password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> None:
    auth_service = _auth_service()
    auth_service.logout(session_id=cu.session_id)


@router.get(
    "/",
    response_model=list[UserPublic],
    summary="Récupérer tous les utilisateurs",
    description="Renvoie la liste complète des utilisateurs enregistrés",
    dependencies=[Depends(get_current_user_checked_exists)],
)
def get_all_users() -> list[UserPublic]:
    user_service = UserService()
    users = (
        user_service.get_all_users()
    )  # Vous devrez créer cette méthode dans UserService

    return [
        UserPublic(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            status=u.status,
        )
        for u in users
    ]
