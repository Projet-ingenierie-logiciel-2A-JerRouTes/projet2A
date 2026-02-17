from __future__ import annotations

from typing import Protocol

from src.backend.business_objects.recipe import Recipe
from src.backend.clients.spoonacular_client import (
    fetch_detailed_recipes_by_ingredients,
)
from src.backend.services.find_recipe import FindRecipe, IngredientSearchQuery


class RecipeWriteDao(Protocol):
    """Sous-ensemble du DAO nécessaire pour 'cacher' les recettes externes en BDD."""

    def list_recipes(
        self,
        *,
        fk_user_id: int | None = None,
        name_ilike: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recipe]: ...

    def create_recipe(
        self,
        *,
        fk_user_id: int | None,
        name: str,
        status: str | None = "draft",
        prep_time: int | None = 0,
        portion: int | None = 1,
        description: str | None = None,
        ingredient_items=None,
        tag_ids=None,
    ) -> Recipe: ...


class ApiFindRecipe(FindRecipe):
    def __init__(self, api_key: str, *, dao: RecipeWriteDao | None = None):
        self._api_key = api_key
        self._dao = dao

    def get_by_id(self, _recipe_id: int) -> Recipe | None:
        """Lookup par id."""

        # On renvoie None explicitement pour éviter des incohérences silencieuses.
        return None

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

        # Si pas de DAO -> juste renvoyer des BO
        if self._dao is None:
            return [self._detailed_to_bo(r) for r in detailed]

        # Sinon : on persiste en BDD au passage
        saved: list[Recipe] = []
        for r in detailed:
            saved.append(self._get_or_create_local_recipe(r))
        return saved

    @staticmethod
    def _detailed_to_bo(r) -> Recipe:
        recipe = Recipe(
            recipe_id=int(r.id),
            creator_id=0,
            status="public",
            prep_time=int(r.ready_in_minutes or 0),
            portions=int(r.servings or 1),
        )
        recipe.add_translation("en", r.title, "")

        if r.steps:
            text = "\n".join(f"{st.number}. {st.step}" for st in r.steps)
            recipe.add_translation("en_steps", r.title, text)

        return recipe

    def _get_or_create_local_recipe(self, r) -> Recipe:
        """Crée la recette en BDD si pas déjà présente (déduplication par titre)."""
        assert self._dao is not None

        title = (r.title or "").strip()

        # 1) Tentative de retrouver une recette existante via le titre
        if title:
            candidates = self._dao.list_recipes(name_ilike=title, limit=10, offset=0)
            for c in candidates:
                # en BDD la DAO met le texte dans translations["fr"]["name"]
                fr_name = (c.translations.get("fr") or {}).get("name", "")
                if fr_name.strip().lower() == title.lower():
                    return c

        # 2) Sinon : créer
        description_parts: list[str] = []
        if getattr(r, "source_url", None):
            description_parts.append(f"Source: {r.source_url}")
        if getattr(r, "summary", None):
            description_parts.append(str(r.summary))
        if getattr(r, "steps", None):
            steps_txt = "\n".join(
                f"{st.number}. {st.step}"
                for st in sorted(r.steps, key=lambda s: s.number)
            )
            if steps_txt.strip():
                description_parts.append("\nPréparation:\n" + steps_txt)

        description = (
            "\n\n".join(p for p in description_parts if p and str(p).strip()) or None
        )

        created = self._dao.create_recipe(
            fk_user_id=None,
            name=title or "(Sans titre)",
            status="public",
            prep_time=int(getattr(r, "ready_in_minutes", 0) or 0),
            portion=int(getattr(r, "servings", 1) or 1),
            description=description,
        )

        # optionnel : conserver aussi une traduction EN
        created.add_translation("en", title, description or "")
        return created
