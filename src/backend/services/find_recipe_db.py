from __future__ import annotations

from typing import Protocol

from src.backend.business_objects.recipe import Recipe
from src.backend.business_objects.user import GenericUser
from src.backend.services.find_recipe import FindRecipe, IngredientSearchQuery


class RecipeDao(Protocol):
    def get_recipe_by_id(self, recipe_id: int) -> dict | None: ...
    def find_recipes_by_ingredients(
        self, ingredients: list[str], limit: int, max_missing: int
    ) -> list[dict]: ...


class DbFindRecipe(FindRecipe):
    def __init__(self, dao: RecipeDao):
        self._dao = dao

    @staticmethod
    def _to_creator(creator_id: int) -> GenericUser:
        cid = int(creator_id or 0)
        return GenericUser(
            id_user=cid,
            pseudo=f"user{cid}" if cid != 0 else "system",
            password="____",
        )

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        row = self._dao.get_recipe_by_id(recipe_id)
        if row is None:
            return None

        creator = self._to_creator(int(row["creator_id"]))
        return Recipe(
            recipe_id=int(row["recipe_id"]),
            creator=creator,
            status=str(row["status"]),
            prep_time=int(row["prep_time"]),
            portions=int(row["portions"]),
        )

    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        ings = [s.strip().lower() for s in query.ingredients if s and s.strip()]
        if not ings:
            return []
        rows = self._dao.find_recipes_by_ingredients(
            ings, query.limit, query.max_missing
        )

        res: list[Recipe] = []
        for r in rows:
            creator = self._to_creator(int(r["creator_id"]))
            res.append(
                Recipe(
                    recipe_id=int(r["recipe_id"]),
                    creator=creator,
                    status=str(r["status"]),
                    prep_time=int(r["prep_time"]),
                    portions=int(r["portions"]),
                )
            )
        return res
