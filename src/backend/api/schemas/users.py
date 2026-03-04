from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    user_id: int
    username: str
    email: str
    status: str


class MeResponse(BaseModel):
    user: UserPublic


class UpdateMeRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=6, max_length=200)


class UserOut(BaseModel):
    """Réponse simple côté API."""

    user_id: int
    username: str
    email: EmailStr | None = None
    status: str


class UpdateUserRequest(BaseModel):
    """Mise à jour partielle d'un utilisateur (admin ou propriétaire)."""

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None

    # Mot de passe
    old_password: str | None = Field(default=None, min_length=1, max_length=200)
    new_password: str | None = Field(default=None, min_length=6, max_length=200)


class AdminUpdateUserRequest(BaseModel):
    """Mise à jour d'un utilisateur (admin uniquement)."""

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    status: Literal["admin", "user"] | None = None
    reset_password: bool = False


class AdminUpdateUserResponse(BaseModel):
    """Si reset_password=true, le nouveau mot de passe est renvoyé."""

    user: UserPublic
    generated_password: str | None = None
