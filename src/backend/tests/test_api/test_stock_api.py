from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from fastapi.testclient import TestClient
import pytest

from api.deps import get_current_user_checked_exists, get_stock_service
from api.main import app
from services.stock_service import (
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

    resp = client.post("api/stocks", json={"name": "Cuisine"})
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

    resp = client.post("api/stocks", json={"name": ""})
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
    mocker.patch("dao.stock_dao.StockDAO", return_value=stock_dao_instance)

    resp = client.get("api/stocks")
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

    resp = client.get("api/stocks/by-name/Cuisine")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_my_stock_by_name_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.get_user_stock_by_name.return_value = FakeStock(
        id_stock=9, nom="Cuisine"
    )

    resp = client.get("api/stocks/by-name/Cuisine")
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

    resp = client.get("api/stocks/1/lots")
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

    resp = client.get("api/stocks/1/lots")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "nope"


def test_add_lot_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.add_lot.return_value = 123

    resp = client.post(
        "api/stocks/1/lots",
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

    resp = client.delete("api/stocks/lots/10")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    stock_service_mock.delete_lot.assert_called_once_with(user_id=42, stock_item_id=10)


def test_delete_lot_not_found(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.delete_lot.side_effect = NotFoundError("missing")

    resp = client.delete("api/stocks/lots/999")
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

    resp = client.post(
        "api/stocks/1/consume", json={"ingredient_id": 7, "quantity": 2.0}
    )
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

    resp = client.post("api/stocks/1/consume", json={"ingredient_id": 7, "quantity": 0})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad qty"


def mocker_consume_result(stock_id: int, ingredient_id: int, consumed_quantity: float):
    class _Res:
        def __init__(self):
            self.stock_id = stock_id
            self.ingredient_id = ingredient_id
            self.consumed_quantity = consumed_quantity

    return _Res()


def test_delete_stock_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.delete_stock.return_value = True

    resp = client.delete("api/stocks/1")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    stock_service_mock.delete_stock.assert_called_once_with(user_id=42, stock_id=1)


def test_delete_stock_not_found(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.delete_stock.side_effect = NotFoundError("missing")

    resp = client.delete("api/stocks/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "missing"


def test_empty_stock_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.empty_stock.return_value = 3

    resp = client.delete("api/stocks/1/lots")
    assert resp.status_code == 200
    assert resp.json() == {"deleted_lots": 3}

    stock_service_mock.empty_stock.assert_called_once_with(user_id=42, stock_id=1)


def test_empty_stock_forbidden(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.empty_stock.side_effect = ForbiddenError("nope")

    resp = client.delete("api/stocks/1/lots")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "nope"


def test_consume_all_stocks_ok(client, auth_user_override, stock_service_mock):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.consume_fefo_all_stocks.return_value = mocker_consume_all_result(
        ingredient_id=7,
        consumed_quantity=2.0,
        by_stock={1: 1.5, 2: 0.5},
    )

    resp = client.post("api/stocks/consume", json={"ingredient_id": 7, "quantity": 2.0})
    assert resp.status_code == 200
    assert resp.json() == {
        "ingredient_id": 7,
        "consumed_quantity": 2.0,
        "by_stock": {"1": 1.5, "2": 0.5},  # JSON => clés en str
    }

    stock_service_mock.consume_fefo_all_stocks.assert_called_once_with(
        user_id=42,
        ingredient_id=7,
        quantity=2.0,
    )


def test_consume_all_stocks_validation_error(
    client, auth_user_override, stock_service_mock
):
    app.dependency_overrides[get_current_user_checked_exists] = auth_user_override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.consume_fefo_all_stocks.side_effect = ValidationError("bad qty")

    resp = client.post("api/stocks/consume", json={"ingredient_id": 7, "quantity": 0})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad qty"


def mocker_consume_all_result(
    ingredient_id: int, consumed_quantity: float, by_stock: dict[int, float]
):
    class _Res:
        def __init__(self):
            self.ingredient_id = ingredient_id
            self.consumed_quantity = consumed_quantity
            self.by_stock = by_stock

    return _Res()


# ---------------------------------------------------------------------
# admin_get_stocks_by_name (/by-name-admin/{name})
# ---------------------------------------------------------------------


def test_admin_get_stocks_by_name_ok(client, stock_service_mock):
    # ⚠️ Pour cet endpoint, cu doit avoir is_admin()
    class _AdminUser(FakeUser):
        def is_admin(self) -> bool:
            return True

    def _override():
        return _AdminUser(user_id=1, status="admin")

    app.dependency_overrides[get_current_user_checked_exists] = _override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.admin_list_stocks_by_name.return_value = [
        FakeStock(id_stock=3, nom="Frigo"),
        FakeStock(id_stock=8, nom="Frigo"),
    ]

    resp = client.get("api/stocks/by-name-admin/Frigo")
    assert resp.status_code == 200
    assert resp.json() == [
        {"stock_id": 3, "name": "Frigo"},
        {"stock_id": 8, "name": "Frigo"},
    ]

    stock_service_mock.admin_list_stocks_by_name.assert_called_once_with(
        name="Frigo",
        with_items=False,
    )


def test_admin_get_stocks_by_name_empty_returns_empty_list(client, stock_service_mock):
    class _AdminUser(FakeUser):
        def is_admin(self) -> bool:
            return True

    def _override():
        return _AdminUser(user_id=1, status="admin")

    app.dependency_overrides[get_current_user_checked_exists] = _override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.admin_list_stocks_by_name.return_value = []

    resp = client.get("api/stocks/by-name-admin/Inconnu")
    assert resp.status_code == 200
    assert resp.json() == []

    stock_service_mock.admin_list_stocks_by_name.assert_called_once_with(
        name="Inconnu",
        with_items=False,
    )


def test_admin_get_stocks_by_name_forbidden_if_not_admin(client, stock_service_mock):
    # ⚠️ user non-admin doit aussi avoir is_admin()
    class _User(FakeUser):
        def is_admin(self) -> bool:
            return False

    def _override():
        return _User(user_id=42, status="user")

    app.dependency_overrides[get_current_user_checked_exists] = _override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    resp = client.get("api/stocks/by-name-admin/Frigo")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Accès réservé aux administrateurs."

    stock_service_mock.admin_list_stocks_by_name.assert_not_called()


def test_admin_get_stocks_by_name_validation_error(client, stock_service_mock):
    class _AdminUser(FakeUser):
        def is_admin(self) -> bool:
            return True

    def _override():
        return _AdminUser(user_id=1, status="admin")

    app.dependency_overrides[get_current_user_checked_exists] = _override
    app.dependency_overrides[get_stock_service] = lambda: stock_service_mock

    stock_service_mock.admin_list_stocks_by_name.side_effect = ValidationError("bad")

    resp = client.get("api/stocks/by-name-admin/%20%20")  # "  "
    assert resp.status_code == 400
    assert resp.json()["detail"] == "bad"
