"""Tests du service ApiFindRecipe (recherche de recettes via l'API).

Ces tests valident :
- le retour de BO Recipe quand aucun DAO n'est fourni,
- la création en base via DAO quand un DAO est fourni,
- la déduplication (si la recette existe déjà en base).
"""

from __future__ import annotations

from business_objects.recipe import Recipe
from business_objects.user import GenericUser
from services.find_recipe import IngredientSearchQuery
from services.find_recipe_api import ApiFindRecipe


# -------------------------
# Fakes pour simuler l'API
# -------------------------
class Step:
    """Étape de recette simplifiée (fake)."""

    def __init__(self, number: int, step: str):
        """Crée une étape.

        Args:
            number (int): Numéro de l'étape.
            step (str): Contenu de l'étape.
        """
        self.number = number
        self.step = step


class FakeDetailedRecipe:
    """Recette détaillée simplifiée (fake), mimant la structure retournée par l'API."""

    def __init__(
        self,
        *,
        id: int,
        title: str,
        ready_in_minutes: int | None = 10,
        servings: int | None = 2,
        steps: list[Step] | None = None,
        source_url: str | None = None,
        summary: str | None = None,
    ):
        """Crée une recette détaillée fake.

        Args:
            id (int): Identifiant externe (ex: Spoonacular).
            title (str): Titre de la recette.
            ready_in_minutes (int | None): Temps de préparation.
            servings (int | None): Nombre de portions.
            steps (list[Step] | None): Liste d'étapes.
            source_url (str | None): URL source.
            summary (str | None): Résumé.
        """
        self.id = id
        self.title = title
        self.ready_in_minutes = ready_in_minutes
        self.servings = servings
        self.steps = steps or []
        self.source_url = source_url
        self.summary = summary


# --------------------------------
# Fake DAO (BDD en mémoire)
# --------------------------------
class FakeRecipeDAO:
    """DAO fake en mémoire pour simuler la persistance."""

    def __init__(self):
        """Initialise une base en mémoire vide."""
        self._db: list[Recipe] = []
        self.created_calls: list[tuple[str, int, int]] = []

    def list_recipes(
        self, *, name_ilike: str | None = None, limit: int = 50, offset: int = 0
    ):
        """Liste les recettes, éventuellement filtrées par nom FR (contient).

        Args:
            name_ilike (str | None): Motif de recherche sur le nom FR.
            limit (int): Nombre max de résultats.
            offset (int): Décalage.

        Returns:
            list[Recipe]: Recettes correspondant au filtre.
        """
        rows = self._db

        if name_ilike:
            needle = name_ilike.strip().lower()
            filtered: list[Recipe] = []
            for r in rows:
                fr_name = (r.translations.get("fr") or {}).get("name", "")
                if needle in fr_name.lower():
                    filtered.append(r)
            rows = filtered

        return rows[offset : offset + limit]

    def create_recipe(
        self,
        *,
        fk_user_id: int | None,
        name: str,
        status: str | None = "draft",
        prep_time: int | None = 0,
        portion: int | None = 1,
        description: str | None = None,
        _ingredient_items=None,
        _tag_ids=None,
    ) -> Recipe:
        """Crée une recette et la stocke dans la base en mémoire.

        Note:
            Les paramètres `_ingredient_items` et `_tag_ids` sont présents pour coller
            à la signature du DAO réel mais ne sont pas utilisés dans ce fake.

        Args:
            fk_user_id (int | None): Id du créateur.
            name (str): Nom de la recette.
            status (str | None): Statut de la recette.
            prep_time (int | None): Temps de préparation.
            portion (int | None): Nombre de portions.
            description (str | None): Description.

        Returns:
            Recipe: Recette créée (avec un id local).
        """
        new_id = 1000 + len(self._db)

        uid = int(fk_user_id or 0)
        creator = GenericUser(
            id_user=uid,
            pseudo=f"user{uid}" if uid != 0 else "system",
            password="____",
        )

        recipe = Recipe(
            recipe_id=new_id,
            creator=creator,
            status=status or "draft",
            prep_time=int(prep_time or 0),
            portions=int(portion or 1),
        )
        # Le DAO réel met un nom en traduction "fr"
        recipe.add_translation("fr", name, description or "")
        self._db.append(recipe)

        self.created_calls.append((name, int(prep_time or 0), int(portion or 1)))
        return recipe


# =========================
#            TESTS
# =========================
def test_search_by_ingredients_without_dao_returns_bo(monkeypatch):
    """Sans DAO, le service doit retourner des BO Recipe construites depuis l'API."""

    def fake_fetch(**_kwargs):
        return [
            FakeDetailedRecipe(
                id=123,
                title="Pancakes",
                ready_in_minutes=15,
                servings=4,
                steps=[Step(1, "Mix"), Step(2, "Cook")],
            )
        ]

    monkeypatch.setattr(
        "services.find_recipe_api.fetch_detailed_recipes_by_ingredients",
        fake_fetch,
    )

    finder = ApiFindRecipe("fake_key", dao=None)
    query = IngredientSearchQuery(ingredients=["egg", "milk"], limit=5)

    res = finder.search_by_ingredients(query)

    assert len(res) == 1
    assert res[0].recipe_id == 123
    assert res[0].prep_time == 15
    assert res[0].portions == 4


def test_search_by_ingredients_with_dao_creates_in_db(monkeypatch):
    """Avec DAO, le service doit créer une recette en base si elle n'existe pas."""

    def fake_fetch(**_kwargs):
        return [
            FakeDetailedRecipe(
                id=123,
                title="Pancakes",
                ready_in_minutes=15,
                servings=4,
                source_url="http://example.com",
                summary="Nice pancakes",
                steps=[Step(1, "Mix"), Step(2, "Cook")],
            )
        ]

    monkeypatch.setattr(
        "services.find_recipe_api.fetch_detailed_recipes_by_ingredients",
        fake_fetch,
    )

    dao = FakeRecipeDAO()
    finder = ApiFindRecipe("fake_key", dao=dao)
    query = IngredientSearchQuery(ingredients=["egg", "milk"], limit=5)

    res = finder.search_by_ingredients(query)

    assert len(res) == 1
    # ID local (créé par le DAO), pas l'id externe
    assert res[0].recipe_id >= 1000
    assert (res[0].translations.get("fr") or {}).get("name") == "Pancakes"
    assert len(dao.created_calls) == 1
    assert dao.created_calls[0] == ("Pancakes", 15, 4)


def test_search_by_ingredients_with_dao_deduplicates(monkeypatch):
    """Avec DAO, si une recette existe déjà, elle doit être réutilisée (pas recréée)."""

    def fake_fetch(**_kwargs):
        return [
            FakeDetailedRecipe(
                id=999, title="Pancakes", ready_in_minutes=99, servings=9
            )
        ]

    monkeypatch.setattr(
        "services.find_recipe_api.fetch_detailed_recipes_by_ingredients",
        fake_fetch,
    )

    dao = FakeRecipeDAO()
    # On pré-remplit la BDD avec Pancakes
    existing = dao.create_recipe(
        fk_user_id=None,
        name="Pancakes",
        status="public",
        prep_time=15,
        portion=4,
        description="already here",
    )
    assert len(dao.created_calls) == 1

    finder = ApiFindRecipe("fake_key", dao=dao)
    query = IngredientSearchQuery(ingredients=["egg"], limit=5)

    res = finder.search_by_ingredients(query)

    assert len(res) == 1
    # On doit récupérer l'existant
    assert res[0].recipe_id == existing.recipe_id
    # Et on ne doit pas recréer
    assert len(dao.created_calls) == 1
