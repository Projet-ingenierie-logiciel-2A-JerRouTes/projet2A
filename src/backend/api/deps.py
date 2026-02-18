from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.config import settings
from dao.recipe_dao import RecipeDAO
from services.find_recipe import FindRecipe, IngredientSearchQuery
from services.find_recipe_api import ApiFindRecipe
from services.find_recipe_factory import FindRecipeFactory
from services.stock_service import StockService
from services.user_service import UserNotFoundError, UserService
from utils.jwt_utils import (
    JWTExpiredError,
    JWTInvalidTokenError,
    JWTIssuerError,
    decode_jwt,
)


# Schéma "Authorization: Bearer <token>"
bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """
    Représente l'utilisateur authentifié courant,
    extrait du JWT.
    """

    user_id: int
    session_id: int
    status: str


def get_user_service() -> UserService:
    """
    Fournit une instance de UserService.
    (séparable facilement pour tests)
    """
    return UserService()


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008
) -> CurrentUser:
    """
    1) Lit le header Authorization: Bearer <token>
    2) Décode et valide le JWT
    3) Extrait les infos minimales (uid, sid, status)
    """

    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = creds.credentials

    try:
        payload = decode_jwt(
            token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
        )
    except (JWTExpiredError, JWTInvalidTokenError, JWTIssuerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    uid = payload.get("uid")
    sid = payload.get("sid")
    status_ = payload.get("status")

    if (
        not isinstance(uid, int)
        or not isinstance(sid, int)
        or not isinstance(status_, str)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    return CurrentUser(
        user_id=uid,
        session_id=sid,
        status=status_,
    )


def get_current_user_checked_exists(
    cu: CurrentUser = Depends(get_current_user),  # noqa: B008
    user_service: UserService = Depends(get_user_service),  # noqa: B008
) -> CurrentUser:
    """
    Variante plus stricte :
    - JWT valide
    - ET utilisateur toujours présent en BDD
    """

    try:
        user_service.get_user(cu.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return cu


def get_stock_service() -> StockService:
    """Fournit une instance de StockService."""
    return StockService()


# ---------------------------------------------------------------------
# Recettes (FindRecipeFactory = DB + API)
# ---------------------------------------------------------------------


class _DbFindRecipe(FindRecipe):
    """Implémentation DB de FindRecipe basée sur RecipeDAO."""

    def __init__(self, dao: RecipeDAO):
        self._dao = dao

    def get_by_id(self, recipe_id: int):
        return self._dao.get_recipe_by_id(int(recipe_id), with_relations=True)

    def search_by_ingredients(self, query: IngredientSearchQuery):
        return self._dao.find_recipes_by_ingredients(
            query.ingredients,
            limit=query.limit,
            max_missing=query.max_missing,
            strict_only=query.strict_only,
            dish_type=query.dish_type,
        )


class _NoApiFindRecipe(FindRecipe):
    """Fallback API désactivé (pas de clé)."""

    def get_by_id(self, _recipe_id: int):
        return None

    def search_by_ingredients(self, _query: IngredientSearchQuery):
        return []


def get_recipe_finder() -> FindRecipe:
    """Fournit le finder de recettes (orchestration DB + API)."""

    recipe_dao = RecipeDAO()
    db_finder: FindRecipe = _DbFindRecipe(recipe_dao)

    # Si pas de clé Spoonacular, on désactive simplement le fallback API.
    if not settings.api_key_spoonacular:
        api_finder: FindRecipe = _NoApiFindRecipe()
    else:
        api_finder = ApiFindRecipe(api_key=settings.api_key_spoonacular, dao=recipe_dao)

    return FindRecipeFactory(db=db_finder, api=api_finder)
