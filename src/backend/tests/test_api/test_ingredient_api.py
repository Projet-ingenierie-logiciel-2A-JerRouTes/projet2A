from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient
import pytest
from src.backend.api.deps import get_current_user_checked_exists
from src.backend.api.main import app


@dataclass
class FakeUser:
    user_id: int
    status: str


@dataclass
class FakeIngredient:
    id_ingredient: int
    name: str
    unit: object
    id_tags: list[int]


class FakeUnit:
    def __init__(self, value: str):
        self.value = value


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_overrides():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


def test_create_ingredient_forbidden_if_not_admin(client):
    def _override_user():
        return FakeUser(user_id=42, status="user")

    app.dependency_overrides[get_current_user_checked_exists] = _override_user

    resp = client.post(
        "/ingredients", json={"name": "Farine", "unit": "g", "tag_ids": []}
    )
    assert resp.status_code == 403
    assert "admin" in resp.json()["detail"].lower()


def test_create_ingredient_ok_admin(client, mocker):
    def _override_admin():
        return FakeUser(user_id=1, status="admin")

    app.dependency_overrides[get_current_user_checked_exists] = _override_admin

    dao_instance = mocker.Mock()
    dao_instance.create_ingredient.return_value = FakeIngredient(
        id_ingredient=10,
        name="Farine",
        unit=FakeUnit("g"),
        id_tags=[1, 2],
    )

    mocker.patch(
        "src.backend.api.routers.ingredients.IngredientDAO", return_value=dao_instance
    )

    resp = client.post(
        "/ingredients", json={"name": "Farine", "unit": "g", "tag_ids": [1, 2]}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "ingredient_id": 10,
        "name": "Farine",
        "unit": "g",
        "tag_ids": [1, 2],
    }

    dao_instance.create_ingredient.assert_called_once_with(
        name="Farine", unit="g", tag_ids=[1, 2]
    )
