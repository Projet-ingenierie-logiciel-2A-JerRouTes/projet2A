from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "projet2a-api"

    # JWT
    jwt_secret: str = os.getenv(
        "JWT_SECRET", os.getenv("PROJET2A_JWT_SECRET", "CHANGE_ME")
    )
    jwt_issuer: str = os.getenv(
        "JWT_ISSUER", os.getenv("PROJET2A_JWT_ISSUER", "projet2a")
    )

    # Durées de vie des tokens
    access_ttl_minutes: int = int(os.getenv("ACCESS_TTL_MINUTES", "15"))
    refresh_ttl_days: int = int(os.getenv("REFRESH_TTL_DAYS", "7"))

    # CORS (frontend local par défaut)
    cors_allow_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]


settings = Settings()
