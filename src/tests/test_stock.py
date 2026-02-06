from datetime import date, timedelta

import pytest

from src.backend.business_objects.stock import Stock


# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def stock():
    """Retourne un stock nommé avec un ID."""
    return Stock(id_stock=1, nom="Stock Central")


# ---------------------------
# Tests d'ajout
# ---------------------------


def test_add_item_new(stock):
    """Vérifie l'ajout simple d'un StockItem."""
    exp_date = date.today() + timedelta(days=7)
    # On passe id_ingredient=10 et id_lot=101
    stock.add_item(10, 101, 5.0, exp_date)

    assert stock.get_total_quantity(10) == 5.0
    # Vérifie que le StockItem est dans le dictionnaire indexé par ID
    assert len(stock.items_by_ingredient[10]) == 1


def test_add_multiple_lots_sorting(stock):
    """Vérifie que les StockItems sont triés par date de péremption."""
    id_ingr = 20
    date_loin = date.today() + timedelta(days=20)
    date_proche = date.today() + timedelta(days=2)

    stock.add_item(id_ingr, 201, 5, date_loin)
    stock.add_item(id_ingr, 202, 3, date_proche)

    # Le lot qui périme le plus tôt (date_proche) doit être à l'index 0
    assert stock.items_by_ingredient[id_ingr][0].expiry_date == date_proche
    assert stock.get_total_quantity(id_ingr) == 8


# ---------------------------
# Tests de retrait (FEFO)
# ---------------------------


def test_remove_quantity_fefo_logic(stock):
    """Vérifie la consommation chronologique (First Expired First Out)."""
    id_ingr = 30
    date_proche = date.today() + timedelta(days=2)
    date_loin = date.today() + timedelta(days=10)

    stock.add_item(id_ingr, 301, 10, date_proche)  # Lot A (périme tôt)
    stock.add_item(id_ingr, 302, 10, date_loin)  # Lot B (périme tard)

    # On consomme 12 : tout le Lot A et 2 du Lot B
    stock.remove_quantity(id_ingr, 12)

    assert stock.get_total_quantity(id_ingr) == 8
    assert len(stock.items_by_ingredient[id_ingr]) == 1
    assert stock.items_by_ingredient[id_ingr][0].id_lot == 302


def test_remove_quantity_insufficient_stock(stock):
    """Vérifie qu'une erreur est levée si le stock est trop bas."""
    stock.add_item(40, 401, 5, date.today())

    with pytest.raises(ValueError, match="Stock insuffisant"):
        stock.remove_quantity(40, 10)


# ---------------------------
# Tests de validation (Types et Valeurs)
# ---------------------------


def test_add_invalid_quantity(stock):
    """Vérifie que StockItem (via Stock) rejette les quantités négatives."""
    with pytest.raises(ValueError):
        stock.add_item(50, 501, -1, date.today())


def test_add_invalid_id_type(stock):
    """Vérifie la validation des types d'ID dans StockItem."""
    with pytest.raises(TypeError):
        # On passe une chaîne au lieu d'un entier pour l'id_ingredient
        stock.add_item("PasUnInt", 601, 5, date.today())


# ---------------------------
# Tests de consultation
# ---------------------------


def test_get_total_quantity_missing(stock):
    """Vérifie qu'un ID inconnu retourne 0."""
    assert stock.get_total_quantity(999) == 0
