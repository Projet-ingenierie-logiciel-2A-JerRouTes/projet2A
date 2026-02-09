from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.config import settings
from src.backend.api.routers.auth import router as auth_router
from src.backend.api.routers.users import router as users_router


# from src.backend.api.routers.recipes import router as recipes_router  # futur


app = FastAPI(title=settings.app_name)

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
# app.include_router(recipes_router)  # quand ça sera prêt


@app.get("/health")
def health():
    return {"status": "ok"}
