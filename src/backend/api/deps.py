from __future__ import annotations

from dataclasses import dataclass
import os

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

    # L'INDENTATION EST LA CLE ICI :
    def is_admin(self) -> bool:
        """Retourne True si l'utilisateur courant est administrateur."""
        return self.status == "admin"


class _NoApiFindRecipe(FindRecipe):
    """Fallback API désactivé (aucun appel externe)."""

    def get_by_id(self, _recipe_id: int):
        return None

    def search_by_ingredients(self, _query: IngredientSearchQuery):
        return []


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


def is_admin(self) -> bool:
    """Retourne True si l'utilisateur courant est administrateur."""
    return self.status == "admin"


def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008
) -> CurrentUser | None:
    """Même logique que get_current_user, mais retourne None si aucun token n'est fourni."""

    if creds is None or not creds.credentials:
        return None

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


def _running_under_pytest() -> bool:
    # PYTEST_CURRENT_TEST est automatiquement défini pendant l'exécution des tests
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


def get_recipe_finder() -> FindRecipe:
    """Fournit le finder de recettes (orchestration DB + API).

    - En prod/dev normal : DB + Spoonacular (si clé)
    - Sous pytest : DB only (pour ne jamais consommer le quota)
    """
    recipe_dao = RecipeDAO()
    db_finder: FindRecipe = _DbFindRecipe(recipe_dao)

    # ✅ Pendant les tests: on coupe l’API externe quoi qu’il arrive
    # (pour ne jamais consommer les 50 requêtes/jour)
    if _running_under_pytest() and not os.getenv("FORCE_SPOONACULAR_IN_TESTS"):
        api_finder: FindRecipe = _NoApiFindRecipe()
        return FindRecipeFactory(db=db_finder, api=api_finder)

    # Hors tests: comportement normal
    if not settings.api_key_spoonacular:
        api_finder = _NoApiFindRecipe()
    else:
        api_finder = ApiFindRecipe(api_key=settings.api_key_spoonacular, dao=recipe_dao)

    return FindRecipeFactory(db=db_finder, api=api_finder)
