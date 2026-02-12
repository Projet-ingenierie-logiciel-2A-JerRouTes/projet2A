from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    """
    Informations de profil destinées à être exposées publiquement ou au sein de
    l'application. Ne contient aucune donnée sensible (comme le hash du mot de passe).
    """

    user_id: int = Field(
        title="ID Utilisateur",
        description="Identifiant unique de l'utilisateur en base de données",
    )
    username: str = Field(
        title="Pseudo", description="Nom d'affichage choisi par l'utilisateur"
    )
    email: EmailStr = Field(
        title="Adresse Email", description="Contact officiel rattaché au compte"
    )
    status: str = Field(
        title="Statut / Rôle",
        description="Définit les permissions (ex: 'admin', 'user')",
    )


class MeResponse(BaseModel):
    """
    Réponse structurée pour la route d'auto-identification (/me).
    Regroupe les informations de l'utilisateur connecté.
    """

    user: UserPublic = Field(
        description="Objet contenant les détails du profil public de l'utilisateur"
    )


class UpdateMeRequest(BaseModel):
    """
    Schéma de validation pour la procédure de modification du mot de passe.
    """

    old_password: str = Field(
        ...,
        min_length=1,
        max_length=200,
        title="Ancien mot de passe",
        description="Requis pour valider l'identité avant modification",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=200,
        title="Nouveau mot de passe",
        description="Doit respecter les critères de sécurité de l'application",
    )


class ChangePasswordRequest(BaseModel):
    """
    Schéma de validation pour la procédure de modification du mot de passe.
    """

    old_password: str = Field(
        ...,
        min_length=1,
        title="Ancien mot de passe",
        description="Requis pour valider l'identité avant modification",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=200,
        title="Nouveau mot de passe",
        description="Doit respecter les critères de sécurité de l'application",
    )
