from __future__ import annotations

import pytest

from services.find_recipe import IngredientSearchQuery
from services.find_recipe_db import DbFindRecipe


@pytest.fixture
def dao(mocker):
    return mocker.Mock()


@pytest.fixture
def service(dao) -> DbFindRecipe:
    return DbFindRecipe(dao)


# ---------------------------------------------------------------------
# Tests : get_by_id
# ---------------------------------------------------------------------


def test_get_by_id_returns_none_when_not_found(service, dao):
    dao.get_recipe_by_id.return_value = None

    assert service.get_by_id(42) is None
    dao.get_recipe_by_id.assert_called_once_with(42, with_relations=True)


def test_get_by_id_returns_recipe_object(service, dao, mocker):
    fake_recipe = mocker.Mock(name="Recipe")
    dao.get_recipe_by_id.return_value = fake_recipe

    res = service.get_by_id(1)
    assert res is fake_recipe
    dao.get_recipe_by_id.assert_called_once_with(1, with_relations=True)


# ---------------------------------------------------------------------
# Tests : search_by_ingredients
# ---------------------------------------------------------------------


def test_search_by_ingredients_returns_empty_when_no_valid_ingredients(service, dao):
    q1 = IngredientSearchQuery(ingredients=[])
    q2 = IngredientSearchQuery(ingredients=["", "   ", "\n"])

    assert service.search_by_ingredients(q1) == []
    assert service.search_by_ingredients(q2) == []

    dao.find_recipes_by_ingredients.assert_not_called()


def test_search_by_ingredients_normalizes_and_calls_dao(service, dao):
    dao.find_recipes_by_ingredients.return_value = []

    query = IngredientSearchQuery(
        ingredients=["  LAIT  ", "oeuf", "", "   ", "Sucre  "],
        limit=7,
        max_missing=2,
        strict_only=False,
        dish_type=None,
    )

    res = service.search_by_ingredients(query)
    assert res == []

    dao.find_recipes_by_ingredients.assert_called_once_with(
        ["lait", "oeuf", "sucre"],
        limit=7,
        max_missing=2,
        strict_only=False,
        dish_type=None,
    )


def test_search_by_ingredients_passes_through_flags(service, dao):
    dao.find_recipes_by_ingredients.return_value = []

    query = IngredientSearchQuery(
        ingredients=["oeuf"],
        limit=10,
        max_missing=1,
        strict_only=True,
        dish_type="dessert",
    )

    _ = service.search_by_ingredients(query)

    dao.find_recipes_by_ingredients.assert_called_once_with(
        ["oeuf"],
        limit=10,
        max_missing=1,
        strict_only=True,
        dish_type="dessert",
    )


def test_search_by_ingredients_returns_dao_result(service, dao, mocker):
    r1 = mocker.Mock(name="Recipe1")
    r2 = mocker.Mock(name="Recipe2")
    dao.find_recipes_by_ingredients.return_value = [r1, r2]

    query = IngredientSearchQuery(ingredients=["oeuf"], limit=10, max_missing=0)
    res = service.search_by_ingredients(query)

    assert res == [r1, r2]
