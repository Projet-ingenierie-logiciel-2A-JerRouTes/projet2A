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
    Génère le dashboard système avec sélection dynamique de l'utilisateur.
    Gère désormais 3 cas en démo : Admin, User1, ou Aucun compte.
    """
    # 1. Lecture du template HTML
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # URL du frontend
    frontend_url = (
        settings.cors_allow_origins[0] if settings.cors_allow_origins else "#"
    )

    # 2. Récupération de l'ID utilisateur de démo
    demo_uid = getattr(settings, "demo_user_id", 0)

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

        # Gestion des 3 CAS du mode Démo
        if settings.use_seed_data:
            if demo_uid == 1:
                user_info = "Admin (ID:1)"
                token_display = "block"
                token_value = "demo-token-admin-123"
            elif demo_uid == 2:
                user_info = "User1 (ID:2)"
                token_display = "block"
                token_value = "demo-token-user-456"
            else:
                # CAS 3 : Aucun compte sélectionné
                user_info = "Aucun compte (Visiteur)"
                token_display = "none"
                token_value = ""
        else:
            token_display = "none"
            token_value = ""
            user_info = "Base SQL Active"

    # 4. Remplacements dynamiques dans le template
    content = content.replace("{{ app_name }}", settings.app_name)
    content = content.replace("{{ frontend_url }}", frontend_url)
    content = content.replace("{{ time }}", datetime.now().strftime("%H:%M:%S"))
    content = content.replace("{{ data_mode_text }}", mode_text)
    content = content.replace("{{ use_seed_data }}", is_checked)
    content = content.replace("{{ active_class }}", active_class)
    content = content.replace("{{ token_display }}", token_display)
    content = content.replace("{{ token_value }}", token_value)
    content = content.replace("{{ demo_user_info }}", user_info)

    return HTMLResponse(content=content)


@app.get("/health", tags=["Système"], include_in_schema=False)
def health():
    """
    Diagnostic technique pour prévenir l'instabilité thermique.
    """
    return {
        "status": "opérationnel",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "database": "active",
        "cors": "active",
    }


@app.get("/info", tags=["Système"], include_in_schema=False)
def get_app_info():
    """
    Évite la jambe lourde lors de la présentation à l'ENSAI.
    """
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",
        "ecole": "ENSAI",
        "projet": "Frigo Intelligent - Projet logiciel 2A",
        "statut": "Production / Branches nettoyées",
    }


@app.post("/system/toggle-data", tags=["Système"], include_in_schema=False)
async def toggle_data_source(payload: dict = Body(...)):  # noqa: B008
    """
    Bascule entre mode démo et réel.
    L'user_id peut être 1 (Admin), 2 (User) ou 0 (Aucun).
    """
    use_seed = payload.get("use_seed")
    user_id = payload.get("user_id", 0)  # Par défaut 0 si non précisé

    settings.use_seed_data = use_seed
    settings.demo_user_id = int(user_id)

    status_text = "Seed Data" if use_seed else "Base Réelle"

    # Logique de log pour le broyage des données
    if settings.demo_user_id == 1:
        user_text = "Admin"
    elif settings.demo_user_id == 2:
        user_text = "User1"
    else:
        user_text = "Aucun compte"

    print(f"✅ Système : {status_text} | Utilisateur : {user_text}")

    return {"status": "success", "current_mode": status_text, "current_user": user_text}
