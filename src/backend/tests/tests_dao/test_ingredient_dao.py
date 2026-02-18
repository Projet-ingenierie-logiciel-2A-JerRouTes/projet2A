from __future__ import annotations

import pytest

from business_objects.ingredient import Ingredient
from business_objects.unit import Unit
from dao.ingredient_dao import IngredientDAO


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def dao() -> IngredientDAO:
    return IngredientDAO()


@pytest.fixture
def mock_db(mocker):
    """
    Mock complet de DBConnection -> connection -> cursor.

    Compatible avec:
    - with conn.cursor() as cur:
    - cur.execute / cur.executemany / cur.fetchone / cur.fetchall
    """
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    mocker.patch("dao.ingredient_dao.DBConnection", return_value=db)

    return conn, cur


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def ingredient_row(ingredient_id=1, name="Farine", unit="g"):
    return {"ingredient_id": ingredient_id, "name": name, "unit": unit}


def tag_rows(*tag_ids: int):
    return [{"fk_tag_id": t} for t in tag_ids]


def executed_sql_list(cur) -> list[str]:
    return [str(c[0][0]) for c in cur.execute.call_args_list]


# ---------------------------------------------------------------------
# Tests : create_ingredient
# ---------------------------------------------------------------------


def test_create_ingredient_success_without_tags(dao, mock_db):
    conn, cur = mock_db

    # 1) INSERT ... RETURNING ingredient_id
    # 2) SELECT ... WHERE ingredient_id = %s
    cur.fetchone.side_effect = [
        {"ingredient_id": 10},
        ingredient_row(ingredient_id=10, name="Farine", unit="g"),
    ]
    cur.fetchall.return_value = []  # pas de tags

    ingredient = dao.create_ingredient(name="Farine", unit=Unit.GRAM, tag_ids=None)

    assert isinstance(ingredient, Ingredient)
    assert ingredient.id_ingredient == 10
    assert ingredient.name == "Farine"
    assert ingredient.unit == Unit.GRAM
    assert ingredient.id_tags == []

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO ingredient" in s for s in sqls)
    assert any("SELECT ingredient_id, name, unit" in s for s in sqls)
    # _replace_tags ne doit pas être appelée si tag_ids=None
    cur.executemany.assert_not_called()


def test_create_ingredient_success_with_tags(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.side_effect = [
        {"ingredient_id": 42},
        ingredient_row(ingredient_id=42, name="Lait", unit="ml"),
    ]
    # _get_tag_ids() appelle fetchall une fois
    cur.fetchall.return_value = tag_rows(2, 5, 9)

    ingredient = dao.create_ingredient(
        name="Lait",
        unit="ml",  # passe par Unit.from_any()
        tag_ids=[9, 2, 5, 5],  # doublons -> should be unique/sorted en executemany
    )

    assert ingredient.id_ingredient == 42
    assert ingredient.name == "Lait"
    assert ingredient.unit == Unit.MILLILITER
    assert ingredient.id_tags == [2, 5, 9]

    # Vérifie que tags ont été remplacés
    # - delete old
    assert any(
        "DELETE FROM ingredient_tag" in str(c[0][0]) for c in cur.execute.call_args_list
    )
    # - insert new via executemany
    cur.executemany.assert_called_once()
    executemany_args = cur.executemany.call_args[0]
    inserted_pairs = executemany_args[1]
    assert inserted_pairs == [(42, 2), (42, 5), (42, 9)]

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_create_ingredient_rollback_on_error(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.create_ingredient(name="Farine", unit=Unit.GRAM)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : get_ingredient_by_id
# ---------------------------------------------------------------------


def test_get_ingredient_by_id_found_with_tags(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = ingredient_row(ingredient_id=7, name="Sucre", unit="g")
    cur.fetchall.return_value = tag_rows(1, 3)

    ing = dao.get_ingredient_by_id(7, with_tags=True)

    assert ing is not None
    assert ing.id_ingredient == 7
    assert ing.name == "Sucre"
    assert ing.unit == Unit.GRAM
    assert ing.id_tags == [1, 3]

    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()


def test_get_ingredient_by_id_found_without_tags(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = ingredient_row(ingredient_id=7, name="Sucre", unit="g")

    ing = dao.get_ingredient_by_id(7, with_tags=False)

    assert ing is not None
    assert ing.id_tags == []
    # fetchall ne doit pas être appelé (pas de tags)
    cur.fetchall.assert_not_called()


def test_get_ingredient_by_id_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    ing = dao.get_ingredient_by_id(999)
    assert ing is None


# ---------------------------------------------------------------------
# Tests : get_ingredient_by_name
# ---------------------------------------------------------------------


def test_get_ingredient_by_name_found_case_insensitive(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = ingredient_row(
        ingredient_id=11, name="Farine", unit="kg"
    )
    cur.fetchall.return_value = tag_rows(4)

    ing = dao.get_ingredient_by_name("fArInE", with_tags=True)

    assert ing is not None
    assert ing.id_ingredient == 11
    assert ing.name == "Farine"
    assert ing.unit == Unit.KILOGRAM
    assert ing.id_tags == [4]

    sqls = executed_sql_list(cur)
    assert any("WHERE LOWER(name) = LOWER(%s)" in s for s in sqls)


def test_get_ingredient_by_name_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    ing = dao.get_ingredient_by_name("inconnu")
    assert ing is None


# ---------------------------------------------------------------------
# Tests : delete_ingredient
# ---------------------------------------------------------------------


def test_delete_ingredient_success(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 1

    ok = dao.delete_ingredient(3)

    assert ok is True
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("DELETE FROM ingredient" in s for s in sqls)


def test_delete_ingredient_not_deleted(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 0

    ok = dao.delete_ingredient(999)
    assert ok is False

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_delete_ingredient_rollback_on_error(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.delete_ingredient(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
