# src/backend/api/charger_seed.py
import json

from src.backend.api.config import settings


# Chemin vers tes données de test (à adapter selon ton arborescence)
DATA_PATH = "src/backend/api/seed_data.py"


def obtenir_donnees(nom_fichier: str):
    """Charge un fichier JSON si le mode démo est actif."""
    if not settings.use_seed_data:
        return None  # Signal pour dire "Utilise la vraie BDD"

    chemin = DATA_PATH / f"{nom_fichier}.json"
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def simuler_login(login, password):
    """Logique spécifique pour l'authentification en mode démo."""
    utilisateurs = obtenir_donnees("users")
    for u in utilisateurs:
        if u["login"] == login and u["password"] == password:
            return {"access_token": "token_demo_ensai", "token_type": "bearer"}
    return None
