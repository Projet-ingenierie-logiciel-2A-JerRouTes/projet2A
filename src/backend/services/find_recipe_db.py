from __future__ import annotations

from typing import Protocol

from business_objects.recipe import Recipe
from services.find_recipe import FindRecipe, IngredientSearchQuery


class RecipeDao(Protocol):
    def get_recipe_by_id(
        self, recipe_id: int, *, with_relations: bool = True
    ) -> Recipe | None: ...

    def find_recipes_by_ingredients(
        self,
        ingredients: list[str],
        *,
        limit: int = 10,
        max_missing: int = 0,
        strict_only: bool = False,
        dish_type: str | None = None,
    ) -> list[Recipe]: ...


class DbFindRecipe(FindRecipe):
    def __init__(self, dao: RecipeDao):
        self._dao = dao

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        return self._dao.get_recipe_by_id(recipe_id, with_relations=True)

    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        ings = [s.strip().lower() for s in query.ingredients if s and s.strip()]
        if not ings:
            return []

        return self._dao.find_recipes_by_ingredients(
            ings,
            limit=query.limit,
            max_missing=query.max_missing,
            strict_only=query.strict_only,
            dish_type=query.dish_type,
        )
