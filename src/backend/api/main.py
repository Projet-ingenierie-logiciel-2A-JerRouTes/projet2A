from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.backend.api.config import settings
from src.backend.api.routers.auth import router as auth_router

# from src.backend.api.routers.ingredients import router as ingredients_router
# from src.backend.api.routers.stocks import router as stocks_router
from src.backend.api.routers.users import router as users_router


# Initialisation de l'application
app = FastAPI(
    title=settings.app_name,
    description="""
    API de gestion de frigo intelligent.
    Permet la gestion des utilisateurs, la consultation du catalogue d'ingrédients
    et la manipulation des stocks personnels.
    """,
    version="1.0.0",
)

# Configuration CORS pour la communication avec le Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs par domaine (Architecture modulaire)
app.include_router(auth_router)
app.include_router(users_router)
# app.include_router(stocks_router)
# app.include_router(ingredients_router)

# --- ROUTES DE NAVIGATION ET DIAGNOSTIC ---


@app.get("/", tags=["Système"], include_in_schema=False)
def read_root():
    # 1. Déterminer le chemin du fichier HTML
    html_path = Path(__file__).parent / "index.html"

    # 2. Lire le contenu du fichier
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # URL du frontend pour le bouton
    frontend_url = (
        settings.cors_allow_origins[0] if settings.cors_allow_origins else "#"
    )

    # Détermination du texte à afficher selon l'état de 'use_seed_data'
    if settings.use_seed_data is None:
        # État initial au lancement d'Uvicorn
        mode_text = "⚠️ SÉLECTIONNER UN MODE"
        is_checked = "false"  # Le switch reste grisé
    else:
        # État une fois que l'utilisateur a fait un choix
        mode_text = "Mode Démo" if settings.use_seed_data else "Base Réelle"
        is_checked = "true" if settings.use_seed_data else "false"

    # 3. Remplacer les placeholders (les {{ ... }}) par les vraies valeurs
    content = content.replace("{{ app_name }}", settings.app_name)
    content = content.replace("{{ frontend_url }}", frontend_url)
    content = content.replace("{{ time }}", datetime.now().strftime("%H:%M:%S"))

    # NOUVEAUX REMPLACEMENTS
    content = content.replace("{{ data_mode_text }}", mode_text)
    content = content.replace("{{ use_seed_data }}", is_checked)

    return HTMLResponse(content=content)


@app.get(
    "/health",
    tags=["Système"],
    summary="Diagnostic technique",
    response_description="État de santé des services",
)
def health():
    """
    Vérifie l'état opérationnel du moteur FastAPI.
    Prévention de l'**instabilité thermique**.
    """
    return {
        "status": "opérationnel",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "database": "seed_data loaded",
        "cors": "active",
    }


@app.get(
    "/info",
    tags=["Système"],
    summary="Carte d'identité de l'API",
    response_description="Métadonnées du projet",
)
def get_app_info():
    """
    Informations de structure pour le rapport final.
    Évite la **jambe lourde** lors de la présentation.
    """
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",
        "ecole": "ENSAI",
        "projet": "Frigo Intelligent - Projet logiciel 2A",
        "statut": "Production / Branches nettoyées",
        "modules_actifs": ["Auth", "Users", "Stocks", "Ingredients"],
    }


@app.post("/system/toggle-data", tags=["Système"], include_in_schema=False)
async def toggle_data_source(payload: dict = Body(...)):  # noqa: B008
    # On récupère la valeur (true ou false)
    use_seed = payload.get("use_seed")

    if use_seed is None:
        return {"status": "error", "message": "Vous devez choisir un mode."}

    settings.use_seed_data = use_seed
    status_text = "Seed Data (Démo)" if use_seed else "Base de Données (Réelle)"
    print(f"✅ Système initialisé en mode : {status_text}")

    return {
        "status": "success",
        "current_mode": status_text,
    }
