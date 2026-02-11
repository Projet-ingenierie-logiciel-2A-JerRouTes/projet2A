from __future__ import annotations

from datetime import date

import pytest
from src.backend.dao.stock_item_dao import StockItemDAO, StockItemRow


@pytest.fixture
def dao() -> StockItemDAO:
    return StockItemDAO()


@pytest.fixture
def mock_db(mocker):
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    mocker.patch("src.backend.dao.stock_item_dao.DBConnection", return_value=db)

    return conn, cur


def stock_item_row(
    stock_item_id=1,
    fk_stock_id=10,
    fk_ingredient_id=7,
    quantity=2.5,
    expiration_date=None,
    created_at="2026-01-01 10:00:00",
):
    return {
        "stock_item_id": stock_item_id,
        "fk_stock_id": fk_stock_id,
        "fk_ingredient_id": fk_ingredient_id,
        "quantity": quantity,
        "expiration_date": expiration_date,
        "created_at": created_at,
    }


def executed_sql_list(cur) -> list[str]:
    return [str(c[0][0]) for c in cur.execute.call_args_list]


# ---------------------------------------------------------------------
# get_stock_item_by_id
# ---------------------------------------------------------------------


def test_get_stock_item_by_id_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = stock_item_row(stock_item_id=5)

    item = dao.get_stock_item_by_id(5)

    assert isinstance(item, StockItemRow)
    assert item.stock_item_id == 5
    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()


def test_get_stock_item_by_id_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    item = dao.get_stock_item_by_id(999)
    assert item is None


# ---------------------------------------------------------------------
# list_stock_items
# ---------------------------------------------------------------------


def test_list_stock_items_without_filter_orders_fefo(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [
        stock_item_row(stock_item_id=1, expiration_date=date(2026, 1, 10)),
        stock_item_row(stock_item_id=2, expiration_date=None),
    ]

    items = dao.list_stock_items(stock_id=10)

    assert len(items) == 2
    assert items[0].stock_item_id == 1

    sqls = executed_sql_list(cur)
    assert any("WHERE fk_stock_id = %s" in s for s in sqls)
    assert any("ORDER BY" in s and "NULLS LAST" in s for s in sqls)


def test_list_stock_items_with_ingredient_filter(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [stock_item_row(stock_item_id=3, fk_ingredient_id=9)]

    items = dao.list_stock_items(stock_id=10, ingredient_id=9)

    assert len(items) == 1
    assert items[0].fk_ingredient_id == 9

    sqls = executed_sql_list(cur)
    assert any("fk_ingredient_id = %s" in s for s in sqls)


# ---------------------------------------------------------------------
# create_stock_item
# ---------------------------------------------------------------------


def test_create_stock_item_success(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = {"stock_item_id": 123}

    lot_id = dao.create_stock_item(
        stock_id=10,
        ingredient_id=7,
        quantity=1.5,
        expiration_date=date(2026, 2, 1),
    )

    assert lot_id == 123
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO stock_item" in s for s in sqls)
    assert any("RETURNING stock_item_id" in s for s in sqls)


def test_create_stock_item_rollback_on_error(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.create_stock_item(
            stock_id=10,
            ingredient_id=7,
            quantity=1.5,
            expiration_date=None,
        )

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# update_stock_item
# ---------------------------------------------------------------------


def test_update_stock_item_updates_quantity_only(dao, mock_db, _mocker):
    conn, cur = mock_db
    # get_stock_item_by_id() interne -> fetchone
    cur.fetchone.return_value = stock_item_row(stock_item_id=5, quantity=9.0)

    item = dao.update_stock_item(5, quantity=9.0)

    assert item is not None
    assert item.quantity == 9.0

    sqls = executed_sql_list(cur)
    assert any("UPDATE stock_item" in s for s in sqls)
    assert any("quantity = %s" in s for s in sqls)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_update_stock_item_updates_expiration_to_null(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = stock_item_row(stock_item_id=5, expiration_date=None)

    item = dao.update_stock_item(5, expiration_date=None)

    assert item is not None
    sqls = executed_sql_list(cur)
    assert any("expiration_date = %s" in s for s in sqls)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_update_stock_item_no_fields_returns_current(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = stock_item_row(stock_item_id=5)

    item = dao.update_stock_item(5)

    assert item is not None
    # ne doit pas faire UPDATE
    sqls = executed_sql_list(cur)
    assert not any("UPDATE stock_item" in s for s in sqls)
    conn.commit.assert_not_called()


def test_update_stock_item_rollback_on_error(dao, mock_db):
    conn, cur = mock_db
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.update_stock_item(5, quantity=3.0)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# delete_stock_item
# ---------------------------------------------------------------------


def test_delete_stock_item_success(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 1

    ok = dao.delete_stock_item(5)

    assert ok is True
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("DELETE FROM stock_item" in s for s in sqls)


def test_delete_stock_item_not_deleted(dao, mock_db):
    conn, cur = mock_db
    cur.rowcount = 0

    ok = dao.delete_stock_item(999)
    assert ok is False
    conn.commit.assert_called_once()


# ---------------------------------------------------------------------
# consume_quantity_fefo
# ---------------------------------------------------------------------


def test_consume_quantity_fefo_invalid_quantity_raises(dao, _mock_db):
    with pytest.raises(ValueError):
        dao.consume_quantity_fefo(stock_id=10, ingredient_id=7, quantity_to_consume=0)


def test_consume_quantity_fefo_insufficient_stock_raises_and_rollbacks(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [
        {"stock_item_id": 1, "quantity": 1.0},
        {"stock_item_id": 2, "quantity": 1.0},
    ]

    with pytest.raises(ValueError):
        dao.consume_quantity_fefo(stock_id=10, ingredient_id=7, quantity_to_consume=3.0)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_consume_quantity_fefo_partial_on_first_lot(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [
        {"stock_item_id": 1, "quantity": 5.0},
        {"stock_item_id": 2, "quantity": 2.0},
    ]

    dao.consume_quantity_fefo(stock_id=10, ingredient_id=7, quantity_to_consume=3.0)

    # doit faire un UPDATE (lot 1 -> 2.0) et aucun DELETE
    sqls = executed_sql_list(cur)
    assert any("FOR UPDATE" in s for s in sqls)
    assert any("UPDATE stock_item" in s for s in sqls)
    assert not any("DELETE FROM stock_item" in s for s in sqls)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_consume_quantity_fefo_delete_first_lot_then_update_second(dao, mock_db):
    conn, cur = mock_db
    cur.fetchall.return_value = [
        {"stock_item_id": 1, "quantity": 2.0},
        {"stock_item_id": 2, "quantity": 5.0},
    ]

    dao.consume_quantity_fefo(stock_id=10, ingredient_id=7, quantity_to_consume=3.0)

    # doit DELETE lot 1 et UPDATE lot 2
    sqls = executed_sql_list(cur)
    assert any("DELETE FROM stock_item" in s for s in sqls)
    assert any("UPDATE stock_item" in s for s in sqls)

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
