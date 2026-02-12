from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.backend.api.config import settings
from src.backend.api.routers.auth import router as auth_router
from src.backend.api.routers.ingredients import router as ingredients_router
from src.backend.api.routers.stocks import router as stocks_router
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
app.include_router(stocks_router)
app.include_router(ingredients_router)

# --- ROUTES DE NAVIGATION ET DIAGNOSTIC ---


@app.get("/", tags=["Système"], include_in_schema=False)
def read_root():
    """
    Génère le dashboard système avec sélection dynamique de l'utilisateur
    pour le mode démo (Admin vs Generic).
    """
    # 1. Lecture du template HTML
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # URL du frontend
    frontend_url = (
        settings.cors_allow_origins[0] if settings.cors_allow_origins else "#"
    )

    # 2. Récupération de l'ID utilisateur de démo (par défaut 1 si non défini)
    demo_uid = getattr(settings, "demo_user_id", 1)

    # 3. Détermination de l'état du mode de données
    if settings.use_seed_data is None:
        mode_text = "⚠️ SÉLECTIONNER UN MODE"
        is_checked = "false"
        active_class = ""
        token_display = "none"
        token_value = ""
        user_info = "N/A"
    else:
        # Configuration active
        mode_text = "Mode Démo" if settings.use_seed_data else "Base Réelle"
        is_checked = "true" if settings.use_seed_data else "false"
        active_class = "active" if settings.use_seed_data else ""

        # Affichage du token et info utilisateur
        if settings.use_seed_data:
            token_display = "block"
            token_value = "demo-token-123"
            # On prépare le libellé pour le dashboard
            user_info = "Admin (ID:1)" if demo_uid == 1 else "User1 (ID:2)"
        else:
            token_display = "none"
            token_value = ""
            user_info = "Base SQL Active"

    # 4. Remplacements dynamiques
    content = content.replace("{{ app_name }}", settings.app_name)
    content = content.replace("{{ frontend_url }}", frontend_url)
    content = content.replace("{{ time }}", datetime.now().strftime("%H:%M:%S"))
    content = content.replace("{{ data_mode_text }}", mode_text)
    content = content.replace("{{ use_seed_data }}", is_checked)
    content = content.replace("{{ active_class }}", active_class)
    content = content.replace("{{ token_display }}", token_display)
    content = content.replace("{{ token_value }}", token_value)

    # NOUVEAU : Placeholder pour afficher quel utilisateur est simulé
    content = content.replace("{{ demo_user_info }}", user_info)

    return HTMLResponse(content=content)


@app.get(
    "/health",
    tags=["Système"],
    summary="Diagnostic technique",
    response_description="État de santé des services",
    include_in_schema=False,
)
def health():
    """
    Vérifie l'état opérationnel du moteur FastAPI.
    Prévention de l'**instabilité thermique**.
    """
    return {
        "status": "opérationnel",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "database": "active",
        "cors": "active",
    }


@app.get(
    "/info",
    tags=["Système"],
    summary="Carte d'identité de l'API",
    response_description="Métadonnées du projet",
    include_in_schema=False,
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
    """
    Bascule entre mode démo et réel, et définit l'utilisateur actif.
    """
    use_seed = payload.get("use_seed")
    # On récupère l'ID envoyé par le dashboard, par défaut 1 (Admin)
    user_id = payload.get("user_id", 1)

    if use_seed is None:
        return {"status": "error", "message": "Mode manquant."}

    # Mise à jour des réglages globaux
    settings.use_seed_data = use_seed
    settings.demo_user_id = int(user_id)

    status_text = "Seed Data" if use_seed else "Base Réelle"
    user_text = "Admin" if settings.demo_user_id == 1 else "User1"

    print(f"✅ Système : {status_text} | Utilisateur : {user_text}")

    return {"status": "success", "current_mode": status_text, "current_user": user_text}
