"""Factory / façade unifiée de recherche de recettes."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from business_objects.recipe import Recipe
from clients.spoonacular_client import SpoonacularRateLimitError
from services.find_recipe import FindRecipe, IngredientSearchQuery


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FindRecipeFactory(FindRecipe):
    """Implémentation composite de `FindRecipe` (DB + API)."""

    db: FindRecipe
    api: FindRecipe

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        """Retourne une recette par identifiant interne BDD.

        Aucun fallback API n’est effectué car `recipe_id` est une clé interne.
        """
        return self.db.get_by_id(recipe_id)

    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        """Recherche des recettes par ingrédients avec fallback API.

        - DB d'abord
        - si pas assez, complète via API
        - merge + déduplication
        - si quota Spoonacular dépassé => on garde juste la DB
        """
        from_db = self.db.search_by_ingredients(query)
        logger.info(
            "FindRecipeFactory: DB returned %s results (limit=%s)",
            len(from_db),
            query.limit,
        )

        if len(from_db) >= query.limit:
            return from_db[: query.limit]

        remaining = max(0, int(query.limit) - len(from_db))
        if remaining == 0:
            return from_db

        api_query = IngredientSearchQuery(
            ingredients=query.ingredients,
            limit=remaining,
            max_missing=query.max_missing,
            strict_only=query.strict_only,
            dish_type=query.dish_type,
            ignore_pantry=query.ignore_pantry,
        )

        logger.info("FindRecipeFactory: calling API for remaining=%s", remaining)
        try:
            from_api = self.api.search_by_ingredients(api_query)
        except SpoonacularRateLimitError as e:
            logger.warning(
                "External recipe API quota exceeded - using DB results only: %s",
                e,
            )
            from_api = []

        seen: set[int] = set()
        merged: list[Recipe] = []

        for r in [*from_db, *from_api]:
            rid = int(getattr(r, "recipe_id", 0) or 0)
            if rid and rid in seen:
                continue
            if rid:
                seen.add(rid)
            merged.append(r)
            if len(merged) >= query.limit:
                break

        return merged
