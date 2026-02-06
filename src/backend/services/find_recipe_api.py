# src/services/find_recipe_api.py
from __future__ import annotations

from src.backend.clients.spoonacular_client import fetch_detailed_recipes_by_ingredients

from src.backend.business_objects.recipe import Recipe
from src.backend.services.find_recipe import FindRecipe, IngredientSearchQuery


class ApiFindRecipe(FindRecipe):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        raise NotImplementedError(
            "get_by_id n'est pas supporté côté API pour l'instant "
            "(pas de fonction client fetch-by-id)."
        )

    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        ingredients = [s.strip() for s in query.ingredients if s and s.strip()]
        if not ingredients:
            return []

        detailed = fetch_detailed_recipes_by_ingredients(
            api_key=self._api_key,
            ingredients=ingredients,
            n=query.limit,
            dish_type=query.dish_type,
            strict_only=query.strict_only,
            max_missing_ingredients=query.max_missing,
            sort="min-missing-ingredients"
            if query.max_missing > 0
            else "max-used-ingredients",
            ignore_pantry=query.ignore_pantry,
            instructions_required=True,
        )

        return [self._detailed_to_bo(r) for r in detailed]

    @staticmethod
    def _detailed_to_bo(r) -> Recipe:
        """
        r est un DetailedRecipe (dataclass) provenant de spoonacular_client.py
        """
        recipe = Recipe(
            recipe_id=int(r.id),
            creator_id=0,  # pas de créateur local
            status="public",
            prep_time=int(r.ready_in_minutes or 0),
            portions=int(r.servings or 1),
        )

        # On exploite le fait que ta BO a translations
        recipe.add_translation("en", r.title, "")

        # Si tu veux aussi ingédients + steps dans la BO :
        # NOTE: ta BO stocke les ingrédients par ingredient_id (int).
        # Spoonacular fournit des noms, pas vos IDs => il faut un mapping name->id côté BDD.
        #
        # En attendant, tu peux au moins stocker ça en translations/description,
        # ou ajouter un champ "external_ingredients" si vous avez une structure prévue.

        # Exemple minimal: on met les steps dans description
        if r.steps:
            text = "\n".join(f"{st.number}. {st.step}" for st in r.steps)
            recipe.add_translation("en_steps", r.title, text)

        return recipe
