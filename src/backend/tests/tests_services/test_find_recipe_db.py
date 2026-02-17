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


def test_get_by_id_returns_none_when_not_found(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")

    dao.get_recipe_by_id.return_value = None

    assert service.get_by_id(42) is None
    dao.get_recipe_by_id.assert_called_once_with(42)

    # Ne doit pas construire Recipe si None
    recipe_cls.assert_not_called()


def test_get_by_id_maps_row_to_recipe(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")
    user_cls = mocker.patch("services.find_recipe_db.GenericUser")
    fake_user = user_cls.return_value

    dao.get_recipe_by_id.return_value = {
        "recipe_id": 1,
        "creator_id": 10,
        "status": "draft",
        "prep_time": 30,
        "portions": 4,
    }

    _ = service.get_by_id(1)

    dao.get_recipe_by_id.assert_called_once_with(1)

    user_cls.assert_called_once_with(
        id_user=10,
        pseudo="user10",
        password="____",
    )

    recipe_cls.assert_called_once_with(
        recipe_id=1,
        creator=fake_user,
        status="draft",
        prep_time=30,
        portions=4,
    )


def test_get_by_id_casts_types(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")
    user_cls = mocker.patch("services.find_recipe_db.GenericUser")
    fake_user = user_cls.return_value

    dao.get_recipe_by_id.return_value = {
        "recipe_id": "2",
        "creator_id": "11",
        "status": 123,
        "prep_time": "15",
        "portions": "2",
    }

    _ = service.get_by_id(2)

    user_cls.assert_called_once_with(
        id_user=11,
        pseudo="user11",
        password="____",
    )

    recipe_cls.assert_called_once_with(
        recipe_id=2,
        creator=fake_user,
        status="123",
        prep_time=15,
        portions=2,
    )


# ---------------------------------------------------------------------
# Tests : search_by_ingredients
# ---------------------------------------------------------------------


def test_search_by_ingredients_returns_empty_when_no_valid_ingredients(
    service, dao, mocker
):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")

    q1 = IngredientSearchQuery(ingredients=[])
    q2 = IngredientSearchQuery(ingredients=["", "   ", "\n"])

    assert service.search_by_ingredients(q1) == []
    assert service.search_by_ingredients(q2) == []

    dao.find_recipes_by_ingredients.assert_not_called()
    recipe_cls.assert_not_called()


def test_search_by_ingredients_normalizes_and_calls_dao(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")

    dao.find_recipes_by_ingredients.return_value = []

    query = IngredientSearchQuery(
        ingredients=["  LAIT  ", "oeuf", "", "   ", "Sucre  "],
        limit=7,
        max_missing=2,
    )

    res = service.search_by_ingredients(query)
    assert res == []

    dao.find_recipes_by_ingredients.assert_called_once_with(
        ["lait", "oeuf", "sucre"], 7, 2
    )
    recipe_cls.assert_not_called()


def test_search_by_ingredients_maps_rows_to_recipes(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")
    user_cls = mocker.patch("services.find_recipe_db.GenericUser")
    fake_user = user_cls.return_value

    dao.find_recipes_by_ingredients.return_value = [
        {
            "recipe_id": 1,
            "creator_id": 10,
            "status": "draft",
            "prep_time": 30,
            "portions": 4,
        },
        {
            "recipe_id": 2,
            "creator_id": 10,
            "status": "public",
            "prep_time": 10,
            "portions": 2,
        },
    ]

    query = IngredientSearchQuery(ingredients=["oeuf"], limit=10, max_missing=0)
    _ = service.search_by_ingredients(query)

    dao.find_recipes_by_ingredients.assert_called_once_with(["oeuf"], 10, 0)

    # On construit deux fois un user "léger" (même id) -> 2 appels
    assert user_cls.call_count == 2
    user_cls.assert_any_call(id_user=10, pseudo="user10", password="____")

    assert recipe_cls.call_count == 2
    recipe_cls.assert_any_call(
        recipe_id=1, creator=fake_user, status="draft", prep_time=30, portions=4
    )
    recipe_cls.assert_any_call(
        recipe_id=2, creator=fake_user, status="public", prep_time=10, portions=2
    )


def test_search_by_ingredients_casts_types(service, dao, mocker):
    recipe_cls = mocker.patch("services.find_recipe_db.Recipe")
    user_cls = mocker.patch("services.find_recipe_db.GenericUser")
    fake_user = user_cls.return_value

    dao.find_recipes_by_ingredients.return_value = [
        {
            "recipe_id": "5",
            "creator_id": "12",
            "status": 999,
            "prep_time": "45",
            "portions": "6",
        }
    ]

    query = IngredientSearchQuery(ingredients=["Chocolat"], limit=3, max_missing=1)
    _ = service.search_by_ingredients(query)

    user_cls.assert_called_once_with(
        id_user=12,
        pseudo="user12",
        password="____",
    )

    recipe_cls.assert_called_once_with(
        recipe_id=5,
        creator=fake_user,
        status="999",
        prep_time=45,
        portions=6,
    )
