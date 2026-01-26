import pytest

from business_objects.stock import Stock


# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def stock():
    """Retourne un stock vide pour chaque test."""
    return Stock()


# ---------------------------
# Tests
# ---------------------------


def test_add_ingredient_new(stock):
    stock.add_ingredient("Tomate", 5)
    assert stock.ingredients["Tomate"] == 5


def test_add_ingredient_existing(stock):
    stock.add_ingredient("Tomate", 5)
    stock.add_ingredient("Tomate", 3)
    assert stock.ingredients["Tomate"] == 8


def test_remove_ingredient_partial(stock):
    stock.add_ingredient("Tomate", 5)
    stock.remove_ingredient("Tomate", 3)
    assert stock.ingredients["Tomate"] == 2


def test_remove_ingredient_exact(stock):
    stock.add_ingredient("Tomate", 5)
    stock.remove_ingredient("Tomate", 5)
    assert "Tomate" not in stock.ingredients


def test_remove_ingredient_missing(stock):
    stock.remove_ingredient("Tomate", 5)  # doit juste ne rien faire
    assert "Tomate" not in stock.ingredients


def test_update_quantity_new(stock):
    stock.update_quantity("Tomate", 10)
    assert stock.ingredients["Tomate"] == 10


def test_update_quantity_existing(stock):
    stock.add_ingredient("Tomate", 5)
    stock.update_quantity("Tomate", 12)
    assert stock.ingredients["Tomate"] == 12


def test_has_ingredient_true(stock):
    stock.add_ingredient("Tomate", 5)
    assert stock.has_ingredient("Tomate", 3) is True


def test_has_ingredient_false(stock):
    stock.add_ingredient("Tomate", 5)
    assert stock.has_ingredient("Tomate", 6) is False


def test_has_ingredient_missing(stock):
    assert stock.has_ingredient("Tomate", 1) is False
