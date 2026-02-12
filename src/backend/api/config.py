from __future__ import annotations

from dataclasses import dataclass, field
import os


# MODIF 1 : Retrait de 'frozen=True' pour permettre de modifier les réglages
# (comme le switch BDD/Seed Data) pendant que le serveur tourne.
@dataclass(slots=True)
class Settings:
    app_name: str = "projet2a-api"

    # --- MODIF 2 : VARIABLE DE CONTRÔLE DE SOURCE DE DONNÉES ---
    # Cette variable pilote tout le backend. Si True, on utilise les données de test.
    # Si False, on interroge la base de données réelle.
    use_seed_data: bool | None = None  # None = Choix non fait

    # JWT : Clés de chiffrement récupérées depuis l'environnement système.
    jwt_secret: str = os.getenv(
        "JWT_SECRET", os.getenv("PROJET2A_JWT_SECRET", "CHANGE_ME")
    )
    jwt_issuer: str = os.getenv(
        "JWT_ISSUER", os.getenv("PROJET2A_JWT_ISSUER", "projet2a")
    )

    # Durées de vie des tokens pour la gestion des sessions utilisateurs.
    access_ttl_minutes: int = int(os.getenv("ACCESS_TTL_MINUTES", "15"))
    refresh_ttl_days: int = int(os.getenv("REFRESH_TTL_DAYS", "7"))

    # CORS : Liste blanche des adresses frontend autorisées.
    # On nettoie les espaces éventuels pour éviter les erreurs de connexion.
    cors_allow_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv(
                "CORS_ALLOW_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if o.strip()
        ]
    )


# --- INSTANCIATION UNIQUE (SINGLETON) ---
# On crée une seule instance 'settings' partagée par tous les modules.
settings = Settings()
