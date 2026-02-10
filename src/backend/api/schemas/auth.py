from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=200)  # email OU username
    password: str = Field(min_length=1, max_length=200)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    session_id: int
