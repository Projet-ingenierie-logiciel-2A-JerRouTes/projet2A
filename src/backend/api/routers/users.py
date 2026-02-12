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
    UserNotFoundError,
    UserService,
)


# from src.backend.scripts.seed_data import users

router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


def _auth_service() -> AuthService:
    return AuthService(
        jwt_secret=settings.jwt_secret,
        jwt_issuer=settings.jwt_issuer,
        access_ttl_minutes=settings.access_ttl_minutes,
        refresh_ttl_days=settings.refresh_ttl_days,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Récupérer mon profil",
    description="Renvoie les infos de l'utilisateur connecté (Admin ou User1).",
)
@router.get(
    "/me",
    response_model=MeResponse,
    summary="Récupérer mon profil",
    description="Renvoie les informations de l'utilisateur connecté (Admin ou User1).",
)
def get_my_profile(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> MeResponse:
    """
    Récupère le profil. En mode démo, on simule les données depuis seed_data.
    """
    # 1. Gestion du mode démo (Seed Data)
    if settings.use_seed_data:
        # Importation PARESSEUSE pour éviter les logs au démarrage du serveur
        from src.backend.scripts.seed_data import get_demo_data

        # On récupère les données de simulation
        data = get_demo_data()

        # On cherche l'utilisateur correspondant à l'ID actif (Admin ou User1)
        # Si non trouvé, on prend le premier par défaut
        user_seed = next(
            (u for u in data["users"] if u.id_user == cu.user_id), data["users"][0]
        )

        return MeResponse(
            user=UserPublic(
                user_id=user_seed.id_user,
                username=user_seed.pseudo,
                email=user_seed.email,
                status=cu.status,
            )
        )

    # 2. Mode Réel (Base de données PostgreSQL)
    user_service = UserService()
    try:
        user = user_service.get_user(cu.user_id)
        return MeResponse(
            user=UserPublic(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                status=user.status,
            )
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put(
    "/me",  # Changé en PUT pour éviter le conflit avec le GET /me
    response_model=MeResponse,
    summary="Mettre à jour mon profil",
)
def update_my_profile(
    req: UpdateMeRequest,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
) -> MeResponse:
    if settings.use_seed_data:
        # En mode démo, on simule une réussite sans rien changer
        return MeResponse(
            user=UserPublic(
                user_id=cu.user_id,
                username=req.username,
                email=req.email,
                status=cu.status,
            )
        )

    # Logique réelle (Postgres) ici...
    raise HTTPException(status_code=501, detail="Non implémenté hors démo")


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
