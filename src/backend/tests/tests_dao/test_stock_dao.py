from __future__ import annotations

from datetime import date

import pytest
from src.backend.dao.stock_dao import StockDAO


@pytest.fixture
def dao() -> StockDAO:
    return StockDAO()


@pytest.fixture
def mock_db(mocker):
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    mocker.patch("src.backend.dao.stock_dao.DBConnection", return_value=db)

    return conn, cur


def stock_row(stock_id=1, name="Cuisine"):
    return {"stock_id": stock_id, "name": name}


def stock_item_lite_row(
    stock_item_id=11, fk_ingredient_id=7, quantity=2.0, expiration_date=None
):
    return {
        "stock_item_id": stock_item_id,
        "fk_ingredient_id": fk_ingredient_id,
        "quantity": quantity,
        "expiration_date": expiration_date,
    }


def executed_sql_list(cur) -> list[str]:
    return [str(c[0][0]) for c in cur.execute.call_args_list]


# ---------------------------------------------------------------------
# create_stock
# ---------------------------------------------------------------------


def test_create_stock_success(dao, mock_db):
    conn, cur = mock_db

    # INSERT returning
    # _fetch_one_stock -> fetchone
    cur.fetchone.side_effect = [{"stock_id": 5}, stock_row(stock_id=5, name="Cuisine")]

    stock = dao.create_stock(name="Cuisine")

    assert stock.id_stock == 5
    assert stock.nom == "Cuisine"

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO stock" in s for s in sqls)
    assert any("SELECT stock_id, name" in s for s in sqls)


def test_create_stock_rollback_on_error(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.create_stock(name="Cuisine")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# get_stock_by_id
# ---------------------------------------------------------------------


def test_get_stock_by_id_with_items(dao, mock_db):
    conn, cur = mock_db

    # _fetch_one_stock -> fetchone
    cur.fetchone.return_value = stock_row(stock_id=10, name="Cuisine")
    # _fetch_stock_items -> fetchall
    cur.fetchall.return_value = [
        stock_item_lite_row(
            stock_item_id=1, fk_ingredient_id=7, quantity=2.0, expiration_date=None
        ),
        stock_item_lite_row(
            stock_item_id=2,
            fk_ingredient_id=8,
            quantity=1.0,
            expiration_date=date(2026, 1, 1),
        ),
    ]

    stock = dao.get_stock_by_id(10, with_items=True)

    assert stock is not None
    assert stock.id_stock == 10
    assert stock.nom == "Cuisine"
    # on ne dépend pas de la structure interne; on vérifie surtout que la requête lots est faite
    sqls = executed_sql_list(cur)
    assert any("FROM stock_item" in s for s in sqls)


def test_get_stock_by_id_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    stock = dao.get_stock_by_id(999)
    assert stock is None


# ---------------------------------------------------------------------
# list_user_stocks
# ---------------------------------------------------------------------


def test_list_user_stocks_with_filter(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [
        stock_row(stock_id=1, name="Cuisine"),
        stock_row(stock_id=2, name="Garage"),
    ]

    stocks = dao.list_user_stocks(user_id=42, name_ilike="Cu", limit=10, offset=0)

    assert len(stocks) == 2
    assert stocks[0].nom == "Cuisine"

    sqls = executed_sql_list(cur)
    assert any("JOIN user_stock" in s for s in sqls)
    assert any("s.name ILIKE %s" in s for s in sqls)


# ---------------------------------------------------------------------
# get_user_stock_by_name
# ---------------------------------------------------------------------


def test_get_user_stock_by_name_found_without_items(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = stock_row(stock_id=9, name="Cuisine")

    stock = dao.get_user_stock_by_name(user_id=42, name="cUiSiNe", with_items=False)

    assert stock is not None
    assert stock.id_stock == 9
    assert stock.nom == "Cuisine"

    sqls = executed_sql_list(cur)
    assert any("LOWER(s.name) = LOWER(%s)" in s for s in sqls)
    # sans items, pas de SELECT sur stock_item
    assert not any("FROM stock_item" in s for s in sqls)


def test_get_user_stock_by_name_found_with_items(dao, mock_db):
    conn, cur = mock_db

    # 1) get_user_stock_by_name -> fetchone
    cur.fetchone.return_value = stock_row(stock_id=9, name="Cuisine")
    # 2) _fetch_stock_items -> fetchall
    cur.fetchall.return_value = [
        stock_item_lite_row(stock_item_id=1, fk_ingredient_id=7, quantity=2.0),
    ]

    stock = dao.get_user_stock_by_name(user_id=42, name="Cuisine", with_items=True)

    assert stock is not None
    sqls = executed_sql_list(cur)
    assert any("FROM stock_item" in s for s in sqls)


def test_get_user_stock_by_name_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    stock = dao.get_user_stock_by_name(user_id=42, name="Inconnu")
    assert stock is None


# ---------------------------------------------------------------------
# add_stock_to_user
# ---------------------------------------------------------------------


def test_add_stock_to_user_inserted(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 1

    inserted = dao.add_stock_to_user(user_id=42, stock_id=7)
    assert inserted is True

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO user_stock" in s for s in sqls)
    assert any("ON CONFLICT DO NOTHING" in s for s in sqls)


def test_add_stock_to_user_already_exists(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 0

    inserted = dao.add_stock_to_user(user_id=42, stock_id=7)
    assert inserted is False
    conn.commit.assert_called_once()


# ---------------------------------------------------------------------
# delete_stock
# ---------------------------------------------------------------------


def test_delete_stock_success(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 1

    ok = dao.delete_stock(5)
    assert ok is True

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("DELETE FROM stock" in s for s in sqls)
