from __future__ import annotations

from unittest.mock import Mock

import pytest
from src.backend.business_objects.recipe import Recipe
from src.backend.business_objects.user import GenericUser
from src.backend.services.find_recipe import IngredientSearchQuery
from src.backend.services.find_recipe_factory import FindRecipeFactory


@pytest.fixture
def db():
    return Mock()


@pytest.fixture
def api():
    return Mock()


@pytest.fixture
def finder(db, api) -> FindRecipeFactory:
    return FindRecipeFactory(db=db, api=api)


def _user(uid: int) -> GenericUser:
    return GenericUser(id_user=uid, pseudo=f"user{uid}", password="____")


def test_get_by_id_uses_db_first_when_found(finder, db, api):
    r = Recipe(
        recipe_id=1,
        creator=_user(1),
        status="draft",
        prep_time=0,
        portions=1,
    )
    db.get_by_id.return_value = r

    assert finder.get_by_id(1) is r
    db.get_by_id.assert_called_once_with(1)
    api.get_by_id.assert_not_called()


def test_get_by_id_does_not_fall_back_to_api_in_case_b(finder, db, api):
    db.get_by_id.return_value = None

    assert finder.get_by_id(99) is None
    db.get_by_id.assert_called_once_with(99)
    api.get_by_id.assert_not_called()


def test_search_by_ingredients_returns_db_if_enough(finder, db, api):
    q = IngredientSearchQuery(ingredients=["egg"], limit=2)
    db.search_by_ingredients.return_value = [
        Recipe(recipe_id=1, creator=_user(1), status="draft", prep_time=0, portions=1),
        Recipe(recipe_id=2, creator=_user(1), status="draft", prep_time=0, portions=1),
    ]

    res = finder.search_by_ingredients(q)
    assert len(res) == 2
    api.search_by_ingredients.assert_not_called()


def test_search_by_ingredients_completes_with_api_when_not_enough(finder, db, api):
    q = IngredientSearchQuery(ingredients=["egg"], limit=3)
    db.search_by_ingredients.return_value = [
        Recipe(recipe_id=1, creator=_user(1), status="draft", prep_time=0, portions=1),
    ]
    api.search_by_ingredients.return_value = [
        Recipe(
            recipe_id=2, creator=_user(0), status="public", prep_time=10, portions=2
        ),
        Recipe(
            recipe_id=3, creator=_user(0), status="public", prep_time=15, portions=2
        ),
    ]

    res = finder.search_by_ingredients(q)
    assert [r.recipe_id for r in res] == [1, 2, 3]
    api.search_by_ingredients.assert_called_once()


def test_search_by_ingredients_deduplicates_ids(finder, db, api):
    q = IngredientSearchQuery(ingredients=["egg"], limit=3)
    db.search_by_ingredients.return_value = [
        Recipe(recipe_id=1, creator=_user(1), status="draft", prep_time=0, portions=1),
        Recipe(recipe_id=2, creator=_user(1), status="draft", prep_time=0, portions=1),
    ]
    api.search_by_ingredients.return_value = [
        Recipe(
            recipe_id=2, creator=_user(0), status="public", prep_time=10, portions=2
        ),
        Recipe(
            recipe_id=3, creator=_user(0), status="public", prep_time=15, portions=2
        ),
    ]

    res = finder.search_by_ingredients(q)
    assert [r.recipe_id for r in res] == [1, 2, 3]
