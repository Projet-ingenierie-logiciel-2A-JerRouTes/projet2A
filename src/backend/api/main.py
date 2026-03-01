from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx

from api.config import settings
from api.routers.auth import router as auth_router
from api.routers.ingredients import router as ingredients_router
from api.routers.recipes import router as recipes_router
from api.routers.stocks import router as stocks_router
from api.routers.users import router as users_router


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(title=settings.app_name)

logger.info("App starting: app_name=%s", settings.app_name)
logger.info("Spoonacular key loaded: %s", bool(settings.api_key_spoonacular))

# CORS (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers par domaine
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(stocks_router)
app.include_router(ingredients_router)
app.include_router(recipes_router)


@app.get("/", tags=["Système"], include_in_schema=False)
def dashboard():
    """
    Affiche le dashboard système à la racine de l'API.
    """
    # Chemin vers ton fichier index.html
    html_path = Path(__file__).parent / "index.html"

    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # Détermination de l'URL du frontend
    frontend_url = (
        settings.cors_allow_origins[0] if settings.cors_allow_origins else "#"
    )

    # Préparation des données de remplacement
    replacements = {
        "{{ app_name }}": settings.app_name,
        "{{ frontend_url }}": frontend_url,
        "{{ time }}": datetime.now().strftime("%H:%M:%S"),
        "{{ data_mode_text }}": "Base de Données Réelle (PostgreSQL)",
        "{{ demo_user_info }}": """
            <ul style='list-style-type: disc; margin: 10px 0; padding-left: 20px; text-align: left; color: #475569;'>
                <li><b>admin</b> : mdpAdmin123</li>
                <li><b>alice</b> : mdpAlice123</li>
                <li><b>bob</b> : mdpBob123</li>
            </ul>
        """,
    }
    # Application des remplacements
    for key, value in replacements.items():
        content = content.replace(key, str(value))

    return HTMLResponse(content=content)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/spoonacular", tags=["Système"])
def health_spoonacular():
    """
    Teste une requête réelle vers Spoonacular.
    Retourne ok si on obtient une réponse HTTP (même erreur quota),
    et donne le status_code.
    """
    if not settings.api_key_spoonacular:
        raise HTTPException(
            status_code=500, detail="Spoonacular API key not configured"
        )

    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": settings.api_key_spoonacular,
        "number": 1,  # on demande 1 résultat
        "query": "pasta",  # requête simple
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
        logger.info("Spoonacular test call done: status=%s", resp.status_code)
        return {
            "spoonacular_reachable": True,
            "status_code": resp.status_code,
        }
    except Exception as e:
        logger.exception("Spoonacular test call failed")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach Spoonacular: {e}",
        ) from e
