from datetime import date, timedelta

import pytest

from src.backend.business_objects.stock_item import StockItem


# ---------------------------
# Tests d'Initialisation
# ---------------------------


def test_stock_item_creation_success():
    """Vérifie qu'un StockItem valide est créé correctement."""
    expiry = date.today() + timedelta(days=10)
    item = StockItem(id_ingredient=1, id_lot=101, quantity=5.5, expiry_date=expiry)

    assert item.id_ingredient == 1
    assert item.id_lot == 101
    assert item.quantity == 5.5
    assert item.expiry_date == expiry


def test_stock_item_invalid_quantity():
    """Vérifie qu'une quantité négative lève une ValueError."""
    with pytest.raises(ValueError, match="La quantité ne peut pas être négative"):
        StockItem(1, 101, -1.0, date.today())


def test_stock_item_invalid_types():
    """Vérifie la validation des types pour chaque argument."""
    expiry = date.today()

    # Test id_ingredient non entier
    with pytest.raises(TypeError):
        StockItem("1", 101, 5.0, expiry)

    # Test expiry_date n'est pas une date
    with pytest.raises(TypeError):
        StockItem(1, 101, 5.0, "2026-01-01")


# ---------------------------
# Tests Logique Métier
# ---------------------------


def test_is_expired_true():
    """Vérifie qu'un lot avec une date passée est considéré comme périmé."""
    hier = date.today() - timedelta(days=1)
    item = StockItem(1, 101, 5.0, hier)
    assert item.is_expired() is True


def test_is_expired_false():
    """Vérifie qu'un lot avec une date future n'est pas périmé."""
    demain = date.today() + timedelta(days=1)
    item = StockItem(1, 101, 5.0, demain)
    assert item.is_expired() is False


# ---------------------------
# Tests Représentation
# ---------------------------


def test_stock_item_repr():
    """Vérifie que le __repr__ contient les informations clés pour le debug."""
    expiry = date(2026, 12, 31)
    item = StockItem(id_ingredient=1, id_lot=101, quantity=10.0, expiry_date=expiry)
    repr_str = repr(item)

    assert "id_lot=101" in repr_str
    assert "id_ingredient=1" in repr_str
    assert "quantity=10.0" in repr_str
