from __future__ import annotations

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
