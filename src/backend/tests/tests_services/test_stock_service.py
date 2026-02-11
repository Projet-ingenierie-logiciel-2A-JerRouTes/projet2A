from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest
from src.backend.services.stock_service import (
    ConsumeResult,
    ForbiddenError,
    NotFoundError,
    StockService,
    ValidationError,
)


# ---------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------


@dataclass
class FakeStock:
    id_stock: int
    nom: str


@pytest.fixture
def mock_db_ownership(mocker):
    """
    Mock DBConnection utilisé uniquement par StockService._user_owns_stock().

    - conn.cursor() utilisé en context manager
    - cur.fetchone() => None (pas owner) ou {"?": 1} (owner)
    """
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    mocker.patch("src.backend.services.stock_service.DBConnection", return_value=db)

    return conn, cur


@pytest.fixture
def mocked_daos(mocker):
    stock_dao = mocker.Mock(name="StockDAO")
    stock_item_dao = mocker.Mock(name="StockItemDAO")
    ingredient_dao = mocker.Mock(name="IngredientDAO")
    return stock_dao, stock_item_dao, ingredient_dao


@pytest.fixture
def service(mocked_daos):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    return StockService(
        stock_dao=stock_dao,
        stock_item_dao=stock_item_dao,
        ingredient_dao=ingredient_dao,
    )


# ---------------------------------------------------------------------
# Tests: _assert_positive
# ---------------------------------------------------------------------


def test_assert_positive_rejects_non_numeric(service):
    with pytest.raises(ValidationError):
        service._assert_positive("abc", "quantity")  # type: ignore[arg-type]


def test_assert_positive_rejects_zero(service):
    with pytest.raises(ValidationError):
        service._assert_positive(0, "quantity")


def test_assert_positive_accepts_positive(service):
    service._assert_positive(0.1, "quantity")


# ---------------------------------------------------------------------
# Tests: create_stock_for_user
# ---------------------------------------------------------------------


def test_create_stock_for_user_calls_dao(service, mocked_daos):
    stock_dao, _, _ = mocked_daos

    stock_dao.create_stock.return_value = FakeStock(id_stock=7, nom="Cuisine")

    stock_id = service.create_stock_for_user(user_id=42, name="Cuisine")

    assert stock_id == 7
    stock_dao.create_stock.assert_called_once_with(name="Cuisine")
    stock_dao.add_stock_to_user.assert_called_once_with(user_id=42, stock_id=7)


# ---------------------------------------------------------------------
# Tests: get_user_stock_by_name
# ---------------------------------------------------------------------


def test_get_user_stock_by_name_delegates(service, mocked_daos):
    stock_dao, _, _ = mocked_daos

    expected = FakeStock(id_stock=1, nom="Cuisine")
    stock_dao.get_user_stock_by_name.return_value = expected

    got = service.get_user_stock_by_name(user_id=42, name="Cuisine", with_items=True)

    assert got == expected
    stock_dao.get_user_stock_by_name.assert_called_once_with(
        user_id=42,
        name="Cuisine",
        with_items=True,
    )


# ---------------------------------------------------------------------
# Tests: add_lot
# ---------------------------------------------------------------------


def test_add_lot_invalid_quantity_raises(service, mocked_daos):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos

    with pytest.raises(ValidationError):
        service.add_lot(user_id=42, stock_id=1, ingredient_id=2, quantity=0)

    stock_dao.get_stock_by_id.assert_not_called()
    stock_item_dao.create_stock_item.assert_not_called()
    ingredient_dao.get_ingredient_by_id.assert_not_called()


def test_add_lot_stock_not_found_raises(service, mocked_daos):
    stock_dao, _, _ = mocked_daos
    stock_dao.get_stock_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.add_lot(user_id=42, stock_id=99, ingredient_id=2, quantity=1)

    stock_dao.get_stock_by_id.assert_called_once_with(99, with_items=False)


def test_add_lot_forbidden_if_not_owner(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    conn, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = None  # pas owner

    with pytest.raises(ForbiddenError):
        service.add_lot(user_id=42, stock_id=1, ingredient_id=2, quantity=1)

    # vérifie qu'on a bien check ownership via SQL
    cur.execute.assert_called_once()
    stock_item_dao.create_stock_item.assert_not_called()
    ingredient_dao.get_ingredient_by_id.assert_not_called()


def test_add_lot_ingredient_not_found_raises(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = {"ok": 1}  # owner
    ingredient_dao.get_ingredient_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.add_lot(user_id=42, stock_id=1, ingredient_id=999, quantity=1)

    ingredient_dao.get_ingredient_by_id.assert_called_once_with(999, with_tags=False)
    stock_item_dao.create_stock_item.assert_not_called()


def test_add_lot_success(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = {"ok": 1}  # owner
    ingredient_dao.get_ingredient_by_id.return_value = object()  # exists
    stock_item_dao.create_stock_item.return_value = 123

    lot_id = service.add_lot(
        user_id=42,
        stock_id=1,
        ingredient_id=7,
        quantity=2.5,
        expiration_date=date(2026, 3, 1),
    )

    assert lot_id == 123
    stock_item_dao.create_stock_item.assert_called_once_with(
        stock_id=1,
        ingredient_id=7,
        quantity=2.5,
        expiration_date=date(2026, 3, 1),
    )


# ---------------------------------------------------------------------
# Tests: list_lots
# ---------------------------------------------------------------------


def test_list_lots_stock_not_found(service, mocked_daos):
    stock_dao, _, _ = mocked_daos
    stock_dao.get_stock_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.list_lots(user_id=42, stock_id=1)

    stock_dao.get_stock_by_id.assert_called_once_with(1, with_items=False)


def test_list_lots_forbidden_if_not_owner(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, _ = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = None  # pas owner

    with pytest.raises(ForbiddenError):
        service.list_lots(user_id=42, stock_id=1)

    stock_item_dao.list_stock_items.assert_not_called()


def test_list_lots_success_with_filter(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, _ = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = {"ok": 1}  # owner

    stock_item_dao.list_stock_items.return_value = ["lot1", "lot2"]

    lots = service.list_lots(user_id=42, stock_id=1, ingredient_id=7)

    assert lots == ["lot1", "lot2"]
    stock_item_dao.list_stock_items.assert_called_once_with(
        stock_id=1,
        ingredient_id=7,
        order_fefo=True,
    )


# ---------------------------------------------------------------------
# Tests: delete_lot
# ---------------------------------------------------------------------


def test_delete_lot_not_found(service, mocked_daos):
    _, stock_item_dao, _ = mocked_daos
    stock_item_dao.get_stock_item_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.delete_lot(user_id=42, stock_item_id=999)

    stock_item_dao.delete_stock_item.assert_not_called()


def test_delete_lot_forbidden_if_not_owner(service, mocked_daos, mock_db_ownership):
    _, stock_item_dao, _ = mocked_daos
    _, cur = mock_db_ownership

    # lot existe
    lot = mocker_lot(stock_item_id=5, fk_stock_id=1)
    stock_item_dao.get_stock_item_by_id.return_value = lot

    cur.fetchone.return_value = None  # pas owner

    with pytest.raises(ForbiddenError):
        service.delete_lot(user_id=42, stock_item_id=5)

    stock_item_dao.delete_stock_item.assert_not_called()


def test_delete_lot_success(service, mocked_daos, mock_db_ownership):
    _, stock_item_dao, _ = mocked_daos
    _, cur = mock_db_ownership

    lot = mocker_lot(stock_item_id=5, fk_stock_id=1)
    stock_item_dao.get_stock_item_by_id.return_value = lot
    stock_item_dao.delete_stock_item.return_value = True

    cur.fetchone.return_value = {"ok": 1}  # owner

    ok = service.delete_lot(user_id=42, stock_item_id=5)

    assert ok is True
    stock_item_dao.delete_stock_item.assert_called_once_with(5)


# ---------------------------------------------------------------------
# Tests: consume_fefo
# ---------------------------------------------------------------------


def test_consume_fefo_invalid_quantity(service, mocked_daos):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos

    with pytest.raises(ValidationError):
        service.consume_fefo(user_id=1, stock_id=1, ingredient_id=1, quantity=0)

    stock_dao.get_stock_by_id.assert_not_called()
    stock_item_dao.consume_quantity_fefo.assert_not_called()
    ingredient_dao.get_ingredient_by_id.assert_not_called()


def test_consume_fefo_stock_not_found(service, mocked_daos):
    stock_dao, _, _ = mocked_daos
    stock_dao.get_stock_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.consume_fefo(user_id=1, stock_id=999, ingredient_id=1, quantity=1)

    stock_dao.get_stock_by_id.assert_called_once_with(999, with_items=False)


def test_consume_fefo_forbidden_if_not_owner(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, _ = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = None  # pas owner

    with pytest.raises(ForbiddenError):
        service.consume_fefo(user_id=42, stock_id=1, ingredient_id=7, quantity=1)

    stock_item_dao.consume_quantity_fefo.assert_not_called()


def test_consume_fefo_ingredient_not_found(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = {"ok": 1}  # owner
    ingredient_dao.get_ingredient_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.consume_fefo(user_id=42, stock_id=1, ingredient_id=999, quantity=1)

    stock_item_dao.consume_quantity_fefo.assert_not_called()


def test_consume_fefo_success(service, mocked_daos, mock_db_ownership):
    stock_dao, stock_item_dao, ingredient_dao = mocked_daos
    _, cur = mock_db_ownership

    stock_dao.get_stock_by_id.return_value = FakeStock(id_stock=1, nom="Cuisine")
    cur.fetchone.return_value = {"ok": 1}  # owner
    ingredient_dao.get_ingredient_by_id.return_value = object()  # exists

    result = service.consume_fefo(user_id=42, stock_id=1, ingredient_id=7, quantity=2.0)

    assert isinstance(result, ConsumeResult)
    assert result.stock_id == 1
    assert result.ingredient_id == 7
    assert result.consumed_quantity == 2.0

    stock_item_dao.consume_quantity_fefo.assert_called_once_with(
        stock_id=1,
        ingredient_id=7,
        quantity_to_consume=2.0,
    )


# ---------------------------------------------------------------------
# Small helper: create a fake StockItemRow-like object
# ---------------------------------------------------------------------


def mocker_lot(stock_item_id: int, fk_stock_id: int):
    """
    Retourne un objet qui ressemble à StockItemRow pour le service,
    sans dépendre de la vraie classe/import.
    """

    class Lot:
        def __init__(self):
            self.stock_item_id = stock_item_id
            self.fk_stock_id = fk_stock_id

    return Lot()
