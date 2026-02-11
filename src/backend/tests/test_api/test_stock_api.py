from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from fastapi.testclient import TestClient
import pytest
from src.backend.api.deps import get_current_user_checked_exists, get_stock_service
from src.backend.api.main import app
from src.backend.services.stock_service import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


@dataclass
class FakeUser:
    user_id: int
    status: str


@dataclass
class FakeStock:
    id_stock: int
    nom: str


@dataclass
class FakeLot:
    stock_item_id: int
    fk_stock_id: int
    fk_ingredient_id: int
    quantity: float
    expiration_date: date | None


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_user_override():
    def _override():
        return FakeUser(user_id=42, status="user")

    return _override


@pytest.fixture
def auth_admin_override():
    def _override():
        return FakeUser(user_id=1, status="admin")

    return _override


@pytest.fixture
def stock_service_mock(mocker):
    return mocker.Mock(name="StockService")


@pytest.fixture(autouse=True)
def reset_overrides():
    # Nettoyage automatique entre tests
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


def test_create_stock_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.create_stock_for_user.return_value = 7

    resp = client.post("/stocks", json={"name": "Cuisine"})
    assert resp.status_code == 200
    assert resp.json() == {"stock_id": 7}

    stock_service_mock.create_stock_for_user.assert_called_once_with(
        user_id=42,
        name="Cuisine",
    )


def test_create_stock_validation_error(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.create_stock_for_user.side_effect = ValidationError("bad")

    resp = client.post("/stocks", json={"name": ""})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad"


def test_list_my_stocks_ok(client, auth_user_override, mocker):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override

    # Route utilise StockDAO directement (import local), donc on patch le vrai module
    stock_dao_instance = mocker.Mock()
    stock_dao_instance.list_user_stocks.return_value = [
        FakeStock(id_stock=1, nom="Cuisine"),
        FakeStock(id_stock=2, nom="Garage"),
    ]
    mocker.patch("src.backend.dao.stock_dao.StockDAO", return_value=stock_dao_instance)

    resp = client.get("/stocks")
    assert resp.status_code == 200
    assert resp.json() == [
        {"stock_id": 1, "name": "Cuisine"},
        {"stock_id": 2, "name": "Garage"},
    ]

    stock_dao_instance.list_user_stocks.assert_called_once_with(
        user_id=42,
        name_ilike=None,
        limit=200,
        offset=0,
    )


def test_get_my_stock_by_name_none(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.get_user_stock_by_name.return_value = None

    resp = client.get("/stocks/by-name/Cuisine")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_my_stock_by_name_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.get_user_stock_by_name.return_value = FakeStock(
        id_stock=9, nom="Cuisine"
    )

    resp = client.get("/stocks/by-name/Cuisine")
    assert resp.status_code == 200
    assert resp.json() == {"stock_id": 9, "name": "Cuisine"}


def test_list_lots_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.list_lots.return_value = [
        FakeLot(
            stock_item_id=10,
            fk_stock_id=1,
            fk_ingredient_id=7,
            quantity=2.5,
            expiration_date=date(2026, 3, 1),
        ),
        FakeLot(
            stock_item_id=11,
            fk_stock_id=1,
            fk_ingredient_id=7,
            quantity=1.0,
            expiration_date=None,
        ),
    ]

    resp = client.get("/stocks/1/lots")
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "stock_item_id": 10,
            "stock_id": 1,
            "ingredient_id": 7,
            "quantity": 2.5,
            "expiration_date": "2026-03-01",
        },
        {
            "stock_item_id": 11,
            "stock_id": 1,
            "ingredient_id": 7,
            "quantity": 1.0,
            "expiration_date": None,
        },
    ]

    stock_service_mock.list_lots.assert_called_once_with(
        user_id=42,
        stock_id=1,
        ingredient_id=None,
    )


def test_list_lots_forbidden(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.list_lots.side_effect = ForbiddenError("nope")

    resp = client.get("/stocks/1/lots")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "nope"


def test_add_lot_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.add_lot.return_value = 123

    resp = client.post(
        "/stocks/1/lots",
        json={"ingredient_id": 7, "quantity": 2.5, "expiration_date": "2026-03-01"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"stock_item_id": 123}

    stock_service_mock.add_lot.assert_called_once_with(
        user_id=42,
        stock_id=1,
        ingredient_id=7,
        quantity=2.5,
        expiration_date=date(2026, 3, 1),
    )


def test_delete_lot_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.delete_lot.return_value = True

    resp = client.delete("/stocks/lots/10")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    stock_service_mock.delete_lot.assert_called_once_with(user_id=42, stock_item_id=10)


def test_delete_lot_not_found(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.delete_lot.side_effect = NotFoundError("missing")

    resp = client.delete("/stocks/lots/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "missing"


def test_consume_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.consume_fefo.return_value = mocker_consume_result(
        stock_id=1,
        ingredient_id=7,
        consumed_quantity=2.0,
    )

    resp = client.post("/stocks/1/consume", json={"ingredient_id": 7, "quantity": 2.0})
    assert resp.status_code == 200
    assert resp.json() == {"stock_id": 1, "ingredient_id": 7, "consumed_quantity": 2.0}

    stock_service_mock.consume_fefo.assert_called_once_with(
        user_id=42,
        stock_id=1,
        ingredient_id=7,
        quantity=2.0,
    )


def test_consume_validation_error(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.consume_fefo.side_effect = ValidationError("bad qty")

    resp = client.post("/stocks/1/consume", json={"ingredient_id": 7, "quantity": 0})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad qty"


def mocker_consume_result(stock_id: int, ingredient_id: int, consumed_quantity: float):
    class _Res:
        def __init__(self):
            self.stock_id = stock_id
            self.ingredient_id = ingredient_id
            self.consumed_quantity = consumed_quantity

    return _Res()
