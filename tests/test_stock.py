from datetime import date, timedelta

import pytest

from src.business_objects.ingredient import Ingredient
from src.business_objects.stock import Stock
from src.business_objects.unit import Unit


# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def stock():
    """Retourne un stock vide pour chaque test."""
    return Stock()


@pytest.fixture
def tomate():
    """Retourne un objet Ingredient standard pour les tests."""
    return Ingredient(name="Tomate", unit=Unit.PIECE)


# ---------------------------
# Tests d'ajout
# ---------------------------


def test_add_ingredient_new(stock, tomate):
    exp_date = date.today() + timedelta(days=7)
    stock.add_ingredient(tomate, 5, exp_date)

    assert stock.get_total_quantity("Tomate") == 5
    # Vérifie que le lot a été créé
    assert len(stock.ingredients_by_name["Tomate"]) == 1


def test_add_multiple_lots_sorting(stock, tomate):
    """Vérifie que les lots sont triés par date de péremption."""
    date_loin = date.today() + timedelta(days=20)
    date_proche = date.today() + timedelta(days=2)

    stock.add_ingredient(tomate, 5, date_loin)
    stock.add_ingredient(tomate, 3, date_proche)

    # Le lot qui périme le plus tôt (date_proche) doit être à l'index 0
    assert stock.ingredients_by_name["Tomate"][0].expiry_date == date_proche
    assert stock.get_total_quantity("Tomate") == 8


# ---------------------------
# Tests de retrait (FEFO)
# ---------------------------


def test_remove_quantity_fefo_logic(stock, tomate):
    """Vérifie que le lot le plus ancien est consommé en premier."""
    date_proche = date.today() + timedelta(days=2)
    date_loin = date.today() + timedelta(days=10)

    stock.add_ingredient(tomate, 10, date_proche)  # Lot A
    stock.add_ingredient(tomate, 10, date_loin)  # Lot B

    # On consomme 12 unités : tout le Lot A (10) et une partie du Lot B (2)
    stock.remove_quantity("Tomate", 12)

    assert stock.get_total_quantity("Tomate") == 8
    assert len(stock.ingredients_by_name["Tomate"]) == 1
    assert stock.ingredients_by_name["Tomate"][0].expiry_date == date_loin


def test_remove_quantity_insufficient_stock(stock, tomate):
    """Vérifie qu'une erreur est levée si on demande trop."""
    stock.add_ingredient(tomate, 5, date.today())

    with pytest.raises(ValueError, match="Stock insuffisant"):
        stock.remove_quantity("Tomate", 10)


# ---------------------------
# Tests de validation (Types et Valeurs)
# ---------------------------


def test_add_invalid_quantity(stock, tomate):
    """Vérifie que l'on ne peut pas ajouter une quantité négative."""
    with pytest.raises(ValueError):
        stock.add_ingredient(tomate, -1, date.today())


def test_add_invalid_type(stock):
    """Vérifie que l'argument ingredient doit être un objet Ingredient."""
    with pytest.raises(TypeError):
        stock.add_ingredient("PasUnObjet", 5, date.today())


# ---------------------------
# Tests de consultation
# ---------------------------


def test_get_total_quantity_missing(stock):
    """Vérifie qu'un ingrédient inconnu retourne 0."""
    assert stock.get_total_quantity("Inconnu") == 0
