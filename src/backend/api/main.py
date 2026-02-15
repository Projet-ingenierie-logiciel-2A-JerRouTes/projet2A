# main.py complet
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


app = FastAPI(
    title=settings.app_name,
    description="API de gestion de frigo intelligent.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(stocks_router)
app.include_router(ingredients_router)


@app.get("/", tags=["Système"], include_in_schema=False)
def read_root():
    html_path = Path(__file__).parent / "index.html"
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    frontend_url = (
        settings.cors_allow_origins[0] if settings.cors_allow_origins else "#"
    )
    demo_uid = getattr(settings, "demo_user_id", 0)
    use_demo = settings.use_seed_data

    # --- PRÉPARATION DES STATUTS ---
    backend_val = "CONNECTÉ"

    if use_demo is None:
        mode_text, mode_bullet = "⚠️ SÉLECTIONNER UN MODE", "bullet-off"
        user_info, user_bullet = "N/A", "bullet-off"
        show_nav = "none"
        token_val = ""
    elif use_demo:
        mode_text, mode_bullet = "Mode Démo", "bullet-demo"
        show_nav = "grid"
        if demo_uid == 1:
            user_info, user_bullet, token_val = (
                "Admin (ID:1)",
                "bullet-real",
                "demo-token-admin-123",
            )
        elif demo_uid == 2:
            user_info, user_bullet, token_val = (
                "User1 (ID:2)",
                "bullet-real",
                "demo-token-user-456",
            )
        else:
            user_info, user_bullet, token_val = "Aucun utilisateur", "bullet-off", ""
    else:
        mode_text, mode_bullet = "Base Réelle", "bullet-real"
        user_info, user_bullet = "Base SQL Active", "bullet-real"
        show_nav = "grid"
        token_val = ""

    # --- REMPLACEMENTS ---
    content = content.replace("{{ app_name }}", settings.app_name)
    content = content.replace("{{ frontend_url }}", frontend_url)
    content = content.replace("{{ time }}", datetime.now().strftime("%H:%M:%S"))
    content = content.replace(
        "{{ backend_status }}", backend_val
    )  # Correction backend_status
    content = content.replace("{{ data_mode_text }}", mode_text)
    content = content.replace("{{ mode_bullet }}", mode_bullet)
    content = content.replace("{{ demo_user_info }}", user_info)
    content = content.replace("{{ user_bullet }}", user_bullet)
    content = content.replace("{{ token_value }}", token_val)

    # Gestion de l'affichage des blocs (on remplace les balises Jinja par du CSS inline)
    content = content.replace(
        "{{ show_demo_options }}", "block" if use_demo else "none"
    )
    content = content.replace("{{ show_nav }}", show_nav)
    content = content.replace(
        "{{ show_token }}", "block" if (use_demo and demo_uid > 0) else "none"
    )

    return HTMLResponse(content=content)


@app.post("/system/toggle-data", include_in_schema=False)
async def toggle_data_source(payload: dict = Body(...)):  # noqa: B008
    settings.use_seed_data = payload.get("use_seed")
    settings.demo_user_id = int(payload.get("user_id", 0))
    return {"status": "success"}
