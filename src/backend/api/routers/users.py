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


router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


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


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Récupérer mon profil",
    description="Renvoie les informations détaillées de l'utilisateur actuellement authentifié via le token JWT.",
    response_description="Le profil public de l'utilisateur connecté",
    tags=["Utilisateurs"],
)
def update_me(
    req: UpdateMeRequest,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> MeResponse:
    user_service = UserService()
    """
    Cette route permet au frontend de vérifier la validité du token et de récupérer
    les informations de base de l'utilisateur (username, email, rôle).

    **Sécurité :**
    - Nécessite un Bearer Token valide.
    - L'identité est extraite du jeton, empêchant l'accès aux données d'autrui.
    """
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


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Changer le mot de passe",
    description="Permet à l'utilisateur connecté de modifier son mot de passe après vérification de l'ancien.",
    response_description="Le mot de passe a été mis à jour avec succès",
)
def change_password(
    req: ChangePasswordRequest,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> None:
    """
    Procédure sécurisée de modification du mot de passe.

    - **old_password**: Requis pour prouver l'identité de l'utilisateur.
    - **new_password**: Le nouveau mot de passe qui sera haché via bcrypt.

    Cette route invalide généralement l'ancien contexte de sécurité, bien que les tokens JWT existants
    puissent rester valides jusqu'à leur expiration (sauf si une liste noire de tokens est implémentée).
    """
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


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Déconnexion",
    description="Invalide la session actuelle de l'utilisateur côté serveur.",
    response_description="La session a été révoquée avec succès",
)
def logout(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> None:
    """
    Révoque l'accès pour la session courante.

    Cette action :
    1. Récupère le **session_id** encodé dans le jeton JWT.
    2. Supprime ou marque comme expirée la session correspondante en base de données via le `AuthService`.
    3. Rend le Refresh Token associé inutilisable pour de futurs renouvellements.
    """
    auth_service = _auth_service()
    auth_service.logout(session_id=cu.session_id)
