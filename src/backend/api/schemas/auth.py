from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Schéma de données pour la création d'un nouveau compte utilisateur.
    Contient les informations minimales nécessaires à l'inscription.
    """

    username: str = Field(
        min_length=3,
        max_length=50,
        title="Nom d'utilisateur",
        description="Pseudo unique utilisé pour l'affichage et l'identification",
    )
    email: EmailStr = Field(
        title="Adresse Email",
        description="Email valide servant d'identifiant et pour la récupération de compte",
    )
    password: str = Field(
        min_length=6,
        max_length=200,
        title="Mot de passe",
        description="Mot de passe sécurisé, sera haché via bcrypt avant stockage",
    )


class LoginRequest(BaseModel):
    """
    Schéma requis pour l'authentification.
    Permet une flexibilité sur l'identifiant utilisé (Email ou Username).
    """

    login: str = Field(
        min_length=1,
        max_length=200,
        title="Identifiant",
        description="Peut être soit l'adresse email, soit le pseudo de l'utilisateur",
    )
    password: str = Field(
        min_length=1,
        max_length=200,
        title="Mot de passe",
        description="Le mot de passe associé au compte",
    )


class RefreshRequest(BaseModel):
    """
    Schéma pour la demande de renouvellement des jetons (Token Refresh).
    Utilisé lorsque le jeton d'accès (Access Token) a expiré.
    """

    refresh_token: str = Field(
        min_length=10,
        title="Jeton de rafraîchissement",
        description="Le jeton longue durée permettant de générer un nouvel access_token",
    )


class TokenPairResponse(BaseModel):
    """
    Structure de la réponse envoyée après une authentification réussie.
    Fournit les clés nécessaires pour les requêtes authentifiées.
    """

    access_token: str = Field(
        title="JWT Access",
        description="Le jeton d'accès (Bearer) pour authentifier les appels API",
    )
    refresh_token: str = Field(
        title="JWT Refresh",
        description="Le jeton permettant de renouveler la session sans reconnexion",
    )
    session_id: int = Field(
        title="ID Session",
        description="L'identifiant unique de la session active en base de données",
    )
