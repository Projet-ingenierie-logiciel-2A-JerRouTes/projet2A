from __future__ import annotations

import pytest

from src.backend.dao.recipe_dao import RecipeDAO


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def dao() -> RecipeDAO:
    """Fixture simple : retourne une instance de RecipeDAO."""
    return RecipeDAO()


@pytest.fixture
def mock_db(mocker):
    """
    Mock complet de DBConnection -> connection -> cursor.

    IMPORTANT:
    - Le code de la DAO utilise parfois `with conn.cursor() as cur:` (context manager)
    - Et parfois `cur = conn.cursor()` (sans with) puis `cur.close()`
    Donc on rend le curseur compatible avec les deux styles:
    - cur.__enter__() -> cur
    - cur.__exit__() -> None
    """
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    cur.fetchall.return_value = []

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    # Patch DBConnection dans le module utilisé par la DAO
    mocker.patch("src.backend.dao.recipe_dao.DBConnection", return_value=db)

    return conn, cur


# ---------------------------------------------------------------------
# Helpers données simulées
# ---------------------------------------------------------------------


def recipe_row(
    recipe_id=1,
    fk_user_id=10,
    name="Crêpes",
    status="draft",
    prep_time=30,
    portion=4,
    description="Recette traditionnelle",
    created_at="2026-01-01 12:00:00",
):
    return {
        "recipe_id": recipe_id,
        "fk_user_id": fk_user_id,
        "name": name,
        "status": status,
        "prep_time": prep_time,
        "portion": portion,
        "description": description,
        "created_at": created_at,
    }


def last_executed_sql(cur) -> str:
    return str(cur.execute.call_args[0][0])


def last_executed_params(cur):
    return cur.execute.call_args[0][1] if len(cur.execute.call_args[0]) > 1 else None


# ---------------------------------------------------------------------
# Tests CRUD : create
# ---------------------------------------------------------------------


def test_create_recipe_success_with_relations(dao, mock_db):
    conn, cur = mock_db

    # 1) INSERT recipe RETURNING id
    # 2) SELECT recipe by id
    cur.fetchone.side_effect = [
        {"recipe_id": 1},  # RETURNING
        recipe_row(recipe_id=1),  # SELECT recipe
    ]

    # get_recipe_ingredients -> fetchall
    # get_recipe_tags        -> fetchall
    cur.fetchall.side_effect = [
        [
            {"fk_ingredient_id": 101, "quantity": 500.0},
            {"fk_ingredient_id": 102, "quantity": 4.0},
        ],
        [{"tag_id": 1, "name": "dessert"}, {"tag_id": 3, "name": "rapide"}],
    ]

    recipe = dao.create_recipe(
        fk_user_id=10,
        name="Crêpes",
        status="draft",
        prep_time=30,
        portion=4,
        description="Recette traditionnelle",
        ingredient_items=[(101, 500.0), (102, 4.0)],
        tag_ids=[1, 3],
    )

    # Assertions métier
    assert recipe.recipe_id == 1
    assert recipe.status == "draft"
    assert recipe.prep_time == 30
    assert recipe.portions == 4
    assert recipe.translations["fr"]["name"] == "Crêpes"
    assert recipe.translations["fr"]["description"] == "Recette traditionnelle"
    assert (101, 500.0) in recipe.ingredients
    assert (102, 4.0) in recipe.ingredients
    assert (1, "dessert") in recipe.tags
    assert (3, "rapide") in recipe.tags

    # Assertions techniques
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    # Vérifie que les requêtes principales ont été exécutées
    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("INSERT INTO recipe" in s for s in executed_sql)
    assert any("INSERT INTO recipe_ingredient" in s for s in executed_sql)
    assert any("INSERT INTO recipe_tag" in s for s in executed_sql)
    assert any("FROM recipe" in s and "WHERE recipe_id" in s for s in executed_sql)


def test_create_recipe_success_without_relations(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.side_effect = [
        {"recipe_id": 2},
        recipe_row(recipe_id=2, name="Omelette", portion=2, prep_time=5),
    ]

    # Pas d'ingredients/tags => la DAO ne devrait pas appeler fetchall
    recipe = dao.create_recipe(
        fk_user_id=10,
        name="Omelette",
        status="draft",
        prep_time=5,
        portion=2,
        description=None,
        ingredient_items=None,
        tag_ids=None,
    )

    assert recipe.recipe_id == 2
    assert recipe.translations["fr"]["name"] == "Omelette"
    assert recipe.ingredients == []
    # recipe.tags peut ne pas exister selon ta BO; on teste "au mieux"
    assert getattr(recipe, "tags", []) == []

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_create_recipe_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db

    # Simule une erreur au moment de l'INSERT
    cur.execute.side_effect = RuntimeError("DB down")

    with pytest.raises(RuntimeError, match="DB down"):
        dao.create_recipe(
            fk_user_id=1,
            name="Test",
        )

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests CRUD : read
# ---------------------------------------------------------------------


def test_get_recipe_by_id_not_found(dao, mock_db):
    _conn, cur = mock_db
    cur.fetchone.return_value = None

    recipe = dao.get_recipe_by_id(999, with_relations=True)
    assert recipe is None


def test_get_recipe_by_id_without_relations(dao, mock_db):
    _conn, cur = mock_db
    cur.fetchone.return_value = recipe_row(recipe_id=3, name="Salade", portion=1)

    recipe = dao.get_recipe_by_id(3, with_relations=False)
    assert recipe is not None
    assert recipe.recipe_id == 3
    assert recipe.translations["fr"]["name"] == "Salade"
    assert recipe.ingredients == []
    assert getattr(recipe, "tags", []) == []

    # On ne doit pas avoir fetchall si pas de relations
    cur.fetchall.assert_not_called()


def test_get_recipe_by_id_with_relations(dao, mock_db):
    _conn, cur = mock_db

    cur.fetchone.return_value = recipe_row(recipe_id=4, name="Pâtes", portion=2)
    cur.fetchall.side_effect = [
        [{"fk_ingredient_id": 201, "quantity": 200.0}],
        [{"tag_id": 9, "name": "italien"}],
    ]

    recipe = dao.get_recipe_by_id(4, with_relations=True)

    assert recipe is not None
    assert recipe.recipe_id == 4
    assert (201, 200.0) in recipe.ingredients
    assert (9, "italien") in recipe.tags


# ---------------------------------------------------------------------
# Tests CRUD : list
# ---------------------------------------------------------------------


def test_list_recipes_no_filter(dao, mock_db):
    _conn, cur = mock_db

    cur.fetchall.return_value = [
        recipe_row(recipe_id=1, name="A"),
        recipe_row(recipe_id=2, name="B"),
    ]

    recipes = dao.list_recipes()
    assert len(recipes) == 2
    assert {r.recipe_id for r in recipes} == {1, 2}

    sql = last_executed_sql(cur)
    assert "FROM recipe" in sql
    assert "WHERE" not in sql  # aucun filtre


def test_list_recipes_with_filters_builds_where(dao, mock_db):
    _conn, cur = mock_db

    cur.fetchall.return_value = [recipe_row(recipe_id=1, fk_user_id=10, name="Crêpes")]

    recipes = dao.list_recipes(fk_user_id=10, name_ilike="êp", limit=20, offset=5)
    assert len(recipes) == 1

    sql = last_executed_sql(cur)
    params = last_executed_params(cur)

    assert "WHERE" in sql
    assert "fk_user_id = %s" in sql
    assert "name ILIKE %s" in sql
    # params = (10, "%êp%", 20, 5)
    assert params[0] == 10
    assert params[1] == "%êp%"
    assert params[2] == 20
    assert params[3] == 5


def test_list_recipes_limit_clamped(dao, mock_db):
    _conn, cur = mock_db
    cur.fetchall.return_value = []

    dao.list_recipes(limit=10_000, offset=-3)

    params = last_executed_params(cur)
    # limit clampé à 500, offset >= 0
    assert params[-2] == 500
    assert params[-1] == 0


# ---------------------------------------------------------------------
# Tests CRUD : update
# ---------------------------------------------------------------------


def test_update_recipe_no_fields_returns_current(dao, mock_db):
    _conn, cur = mock_db

    # get_recipe_by_id appelé, donc SELECT
    cur.fetchone.return_value = recipe_row(recipe_id=5, name="Existante")
    recipe = dao.update_recipe(5)  # aucun champ -> retourne la recette actuelle

    assert recipe is not None
    assert recipe.recipe_id == 5
    assert recipe.translations["fr"]["name"] == "Existante"


def test_update_recipe_not_found_returns_none(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 0  # UPDATE n'affecte rien => not found
    result = dao.update_recipe(999, name="X")

    assert result is None
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_update_recipe_partial_success(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1
    cur.fetchone.return_value = recipe_row(recipe_id=6, name="Nouveau", status="public")
    cur.fetchall.side_effect = [[], []]  # relations vides

    recipe = dao.update_recipe(6, name="Nouveau", status="public")

    assert recipe is not None
    assert recipe.status == "public"
    assert recipe.translations["fr"]["name"] == "Nouveau"

    # Vérifie SQL UPDATE contient les bons champs
    update_call = None
    for c in cur.execute.call_args_list:
        if str(c[0][0]).strip().startswith("UPDATE recipe"):
            update_call = c
            break
    assert update_call is not None

    update_sql = str(update_call[0][0])
    assert "name = %s" in update_sql
    assert "status = %s" in update_sql
    assert "prep_time" not in update_sql
    assert "portion" not in update_sql

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_update_recipe_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db

    def explode(*_args, **_kwargs):
        raise RuntimeError("boom")

    cur.execute.side_effect = explode

    with pytest.raises(RuntimeError, match="boom"):
        dao.update_recipe(1, name="X")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests CRUD : delete
# ---------------------------------------------------------------------


def test_delete_recipe_success(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1
    assert dao.delete_recipe(12) is True

    sql = last_executed_sql(cur)
    params = last_executed_params(cur)

    assert "DELETE FROM recipe" in sql
    assert params == (12,)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_delete_recipe_not_found(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 0
    assert dao.delete_recipe(999) is False

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_delete_recipe_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("delete error")

    with pytest.raises(RuntimeError, match="delete error"):
        dao.delete_recipe(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests relations : ingrédients
# ---------------------------------------------------------------------


def test_add_or_update_ingredient_success(dao, mock_db):
    conn, cur = mock_db

    dao.add_or_update_ingredient(recipe_id=1, ingredient_id=101, quantity=2.5)

    sql = last_executed_sql(cur)
    params = last_executed_params(cur)

    assert "INSERT INTO recipe_ingredient" in sql
    assert params == (1, 101, 2.5)
    conn.commit.assert_called_once()


def test_add_or_update_ingredient_rejects_non_positive_quantity(dao):
    with pytest.raises(ValueError, match="quantité doit être positive"):
        dao.add_or_update_ingredient(recipe_id=1, ingredient_id=101, quantity=0)


def test_add_or_update_ingredient_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("upsert ingredient error")

    with pytest.raises(RuntimeError, match="upsert ingredient error"):
        dao.add_or_update_ingredient(1, 101, 1.0)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_remove_ingredient_returns_bool(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1
    assert dao.remove_ingredient(1, 101) is True

    cur.rowcount = 0
    assert dao.remove_ingredient(1, 999) is False

    assert conn.commit.call_count == 2
    conn.rollback.assert_not_called()


def test_remove_ingredient_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("remove ingredient error")

    with pytest.raises(RuntimeError, match="remove ingredient error"):
        dao.remove_ingredient(1, 101)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_replace_ingredients_deletes_then_inserts(dao, mock_db):
    conn, cur = mock_db

    dao.replace_ingredients(1, [(10, 1.0), (20, 2.0)])

    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("DELETE FROM recipe_ingredient" in s for s in executed_sql)
    assert any("INSERT INTO recipe_ingredient" in s for s in executed_sql)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_replace_ingredients_with_empty_list_only_deletes(dao, mock_db):
    conn, cur = mock_db

    dao.replace_ingredients(1, [])

    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("DELETE FROM recipe_ingredient" in s for s in executed_sql)
    assert not any("INSERT INTO recipe_ingredient" in s for s in executed_sql)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_get_recipe_ingredients_with_external_cursor_does_not_close(
    dao, mock_db, mocker
):
    _conn, cur = mock_db
    cur.fetchall.return_value = [
        {"fk_ingredient_id": 101, "quantity": 1.5},
        {"fk_ingredient_id": 102, "quantity": 2.0},
    ]

    close_spy = mocker.spy(cur, "close")

    items = dao.get_recipe_ingredients(1, cursor=cur)
    assert items == [(101, 1.5), (102, 2.0)]

    # Comme on a fourni cursor=cur, la DAO ne doit pas le fermer
    close_spy.assert_not_called()


def test_get_recipe_ingredients_without_cursor_closes(dao, mock_db, mocker):
    _conn, cur = mock_db
    cur.fetchall.return_value = [{"fk_ingredient_id": 101, "quantity": 1.0}]

    close_spy = mocker.spy(cur, "close")

    items = dao.get_recipe_ingredients(1, cursor=None)
    assert items == [(101, 1.0)]
    close_spy.assert_called_once()


# ---------------------------------------------------------------------
# Tests relations : tags
# ---------------------------------------------------------------------


def test_add_tag_success(dao, mock_db):
    conn, cur = mock_db

    dao.add_tag(1, 3)

    sql = last_executed_sql(cur)
    params = last_executed_params(cur)

    assert "INSERT INTO recipe_tag" in sql
    assert params == (1, 3)
    conn.commit.assert_called_once()


def test_add_tag_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("add tag error")

    with pytest.raises(RuntimeError, match="add tag error"):
        dao.add_tag(1, 3)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_remove_tag_returns_bool(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1
    assert dao.remove_tag(1, 3) is True

    cur.rowcount = 0
    assert dao.remove_tag(1, 999) is False

    assert conn.commit.call_count == 2
    conn.rollback.assert_not_called()


def test_remove_tag_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("remove tag error")

    with pytest.raises(RuntimeError, match="remove tag error"):
        dao.remove_tag(1, 3)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_replace_tags_deletes_then_inserts(dao, mock_db):
    conn, cur = mock_db

    dao.replace_tags(1, [1, 2, 3])

    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("DELETE FROM recipe_tag" in s for s in executed_sql)
    assert any("INSERT INTO recipe_tag" in s for s in executed_sql)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_replace_tags_with_empty_list_only_deletes(dao, mock_db):
    conn, cur = mock_db

    dao.replace_tags(1, [])

    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("DELETE FROM recipe_tag" in s for s in executed_sql)
    assert not any("INSERT INTO recipe_tag" in s for s in executed_sql)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_get_recipe_tags_with_external_cursor_does_not_close(dao, mock_db, mocker):
    _conn, cur = mock_db
    cur.fetchall.return_value = [
        {"tag_id": 1, "name": "dessert"},
        {"tag_id": 2, "name": "rapide"},
    ]

    close_spy = mocker.spy(cur, "close")

    tags = dao.get_recipe_tags(1, cursor=cur)
    assert tags == [(1, "dessert"), (2, "rapide")]

    close_spy.assert_not_called()


def test_get_recipe_tags_without_cursor_closes(dao, mock_db, mocker):
    _conn, cur = mock_db
    cur.fetchall.return_value = [{"tag_id": 1, "name": "dessert"}]

    close_spy = mocker.spy(cur, "close")

    tags = dao.get_recipe_tags(1, cursor=None)
    assert tags == [(1, "dessert")]
    close_spy.assert_called_once()


# ---------------------------------------------------------------------
# Tests : comportements "propres" (commit/rollback) sur replace
# ---------------------------------------------------------------------


def test_replace_ingredients_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db

    # La 1ère requête (DELETE) passe, la seconde (INSERT) plante
    def execute_side_effect(sql, _params=None):
        if "INSERT INTO recipe_ingredient" in str(sql):
            raise RuntimeError("insert failed")

    cur.execute.side_effect = execute_side_effect

    with pytest.raises(RuntimeError, match="insert failed"):
        dao.replace_ingredients(1, [(10, 1.0)])

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_replace_tags_rollback_on_exception(dao, mock_db):
    conn, cur = mock_db

    def execute_side_effect(sql, _params=None):
        if "INSERT INTO recipe_tag" in str(sql):
            raise RuntimeError("insert tags failed")

    cur.execute.side_effect = execute_side_effect

    with pytest.raises(RuntimeError, match="insert tags failed"):
        dao.replace_tags(1, [1, 2])

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : recherche de recettes par ingrédients (logique métier & SQL)
# ---------------------------------------------------------------------


def test_find_recipes_by_ingredients_empty_query_returns_empty(dao, mock_db):
    _conn, cur = mock_db

    res = dao.find_recipes_by_ingredients([])
    assert res == []

    # Ne doit même pas exécuter de SQL
    cur.execute.assert_not_called()


def test_find_recipes_by_ingredients_blank_strings_returns_empty(dao, mock_db):
    _conn, cur = mock_db

    res = dao.find_recipes_by_ingredients(["", "   ", "\n"])
    assert res == []

    cur.execute.assert_not_called()


def test_find_recipes_by_ingredients_clamps_limit_and_max_missing(dao, mock_db):
    """
    Vérifie :
    - limit est clampé (min 1, max 200)
    - max_missing est >= 0
    - strict_only force max_missing à 0
    Et vérifie les paramètres passés à la requête SQL.
    """
    _conn, cur = mock_db

    # La requête principale retourne 1 recette
    cur.fetchall.side_effect = [
        [
            {
                "recipe_id": 1,
                "fk_user_id": 10,
                "name": "Crêpes",
                "status": "draft",
                "prep_time": 30,
                "portion": 4,
                "description": "x",
                "created_at": "2026-01-01 12:00:00",
                "matched_count": 1,
            }
        ],
        # get_recipe_ingredients
        [{"fk_ingredient_id": 101, "quantity": 1.0}],
        # get_recipe_tags
        [{"tag_id": 1, "name": "dessert"}],
    ]

    res = dao.find_recipes_by_ingredients(
        ["lait"],
        limit=10_000,  # -> clamp 200
        max_missing=-5,  # -> clamp 0
        strict_only=False,
    )

    assert len(res) == 1

    # Vérifie les paramètres transmis au cur.execute (requête principale)
    # call_args_list[0] correspond à la requête CTE matched
    _sql, params = (
        cur.execute.call_args_list[0][0][0],
        cur.execute.call_args_list[0][0][1],
    )

    # params = (like_terms, *tag_params, n_terms, max_missing, limit)
    assert params[0] == ["%lait%"]
    assert params[-3] == 1  # n_terms
    assert params[-2] == 0  # max_missing clampé
    assert params[-1] == 200  # limit clampé


def test_find_recipes_by_ingredients_strict_only_forces_zero_missing(dao, mock_db):
    _conn, cur = mock_db

    cur.fetchall.side_effect = [
        [
            {
                "recipe_id": 1,
                "fk_user_id": 10,
                "name": "Crêpes",
                "status": "draft",
                "prep_time": 30,
                "portion": 4,
                "description": "x",
                "created_at": "2026-01-01 12:00:00",
                "matched_count": 2,
            }
        ],
        [],  # ingredients
        [],  # tags
    ]

    dao.find_recipes_by_ingredients(
        ["lait", "oeuf"],
        limit=10,
        max_missing=3,
        strict_only=True,  # doit forcer max_missing=0
    )

    sql, params = (
        cur.execute.call_args_list[0][0][0],
        cur.execute.call_args_list[0][0][1],
    )

    assert "WITH matched AS" in sql
    assert params[0] == ["%lait%", "%oeuf%"]


def test_find_recipes_by_ingredients_with_dish_type_adds_tag_filter(dao, mock_db):
    _conn, cur = mock_db

    cur.fetchall.side_effect = [
        [
            {
                "recipe_id": 2,
                "fk_user_id": 11,
                "name": "Brownie",
                "status": "public",
                "prep_time": 45,
                "portion": 6,
                "description": "y",
                "created_at": "2026-01-02 10:00:00",
                "matched_count": 1,
            }
        ],
        [],  # ingredients
        [{"tag_id": 7, "name": "dessert"}],  # tags
    ]

    res = dao.find_recipes_by_ingredients(
        ["chocolat"],
        dish_type="dessert",
        limit=10,
        max_missing=0,
    )
    assert len(res) == 1
    assert res[0].translations["fr"]["name"] == "Brownie"

    sql = cur.execute.call_args_list[0][0][0]
    params = cur.execute.call_args_list[0][0][1]

    # On doit voir les JOIN tag/recipe_tag de filtrage dans le SQL
    assert "JOIN recipe_tag rt_filter" in sql
    assert "JOIN tag t_filter" in sql
    assert "t_filter.name ILIKE %s" in sql

    # Paramètre dish_type inséré après like_terms
    assert params[0] == ["%chocolat%"]
    assert params[1] == "%dessert%"


def test_find_recipes_by_ingredients_loads_relations_per_recipe(dao, mock_db):
    """
    Vérifie que, pour chaque recette retournée par la requête principale,
    la DAO recharge ingrédients + tags via get_recipe_ingredients/get_recipe_tags.
    """
    _conn, cur = mock_db

    # 2 recettes en sortie de la requête principale
    cur.fetchall.side_effect = [
        [
            {
                "recipe_id": 1,
                "fk_user_id": 10,
                "name": "Crêpes",
                "status": "draft",
                "prep_time": 30,
                "portion": 4,
                "description": "x",
                "created_at": "2026-01-01 12:00:00",
                "matched_count": 1,
            },
            {
                "recipe_id": 2,
                "fk_user_id": 10,
                "name": "Omelette",
                "status": "draft",
                "prep_time": 10,
                "portion": 1,
                "description": "y",
                "created_at": "2026-01-01 13:00:00",
                "matched_count": 1,
            },
        ],
        # Pour recipe_id=1 : ingredients
        [{"fk_ingredient_id": 101, "quantity": 1.0}],
        # Pour recipe_id=1 : tags
        [{"tag_id": 1, "name": "rapide"}],
        # Pour recipe_id=2 : ingredients
        [{"fk_ingredient_id": 102, "quantity": 2.0}],
        # Pour recipe_id=2 : tags
        [],
    ]

    res = dao.find_recipes_by_ingredients(["oeuf"], limit=10, max_missing=0)
    assert len(res) == 2

    # La 1ère execute = requête principale
    # Ensuite, par recette : 1 execute pour ingredients + 1 execute pour tags
    executed_sql = [str(c[0][0]) for c in cur.execute.call_args_list]
    assert any("WITH matched AS" in s for s in executed_sql)  # requête principale
    assert sum("FROM recipe_ingredient" in s for s in executed_sql) == 2
    assert sum("FROM recipe_tag rt" in s for s in executed_sql) == 2


def test_find_recipes_by_ingredients_rollback_not_needed_no_commit(dao, mock_db):
    """
    C'est un SELECT-only : pas de commit/rollback attendu.
    On vérifie qu'on ne commit pas (et pas rollback).
    """
    conn, cur = mock_db
    cur.fetchall.side_effect = [[]]  # aucun résultat

    res = dao.find_recipes_by_ingredients(["x"])
    assert res == []

    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()
