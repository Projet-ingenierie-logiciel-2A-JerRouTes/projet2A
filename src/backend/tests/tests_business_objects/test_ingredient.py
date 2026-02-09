import pytest
from src.backend.business_objects.ingredient import Ingredient
from src.backend.business_objects.unit import Unit


# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def ingredient_test():
    """Retourne un ingrédient de base (Farine) pour les tests."""
    return Ingredient(id_ingredient=1, name="Farine", unit=Unit.GRAM, id_tags=[1, 2])


# ---------------------------
# Tests d'Initialisation
# ---------------------------


def test_ingredient_initialization_success(ingredient_test):
    """Vérifie la création correcte de l'ingrédient."""
    assert ingredient_test.id_ingredient == 1
    assert ingredient_test.name == "Farine"
    assert ingredient_test.unit == Unit.GRAM
    assert ingredient_test.id_tags == [1, 2]


def test_ingredient_empty_name():
    """Vérifie qu'on ne peut pas créer un ingrédient sans nom."""
    with pytest.raises(
        ValueError, match="Le nom de l'ingrédient ne peut pas être vide"
    ):
        Ingredient(id_ingredient=2, name="", unit=Unit.PIECE)


def test_ingredient_invalid_unit():
    """Vérifie que l'unité doit être une instance de l'Enum Unit."""
    with pytest.raises(
        TypeError, match="L'argument 'unit' doit être une instance de Unit"
    ):
        Ingredient(
            id_ingredient=3, name="Eau", unit="LITRE"
        )  # Erreur: string au lieu de Enum


# ---------------------------
# Tests de Gestion des Tags
# ---------------------------


def test_add_id_tag_new(ingredient_test):
    """Vérifie l'ajout d'un nouveau tag unique."""
    ingredient_test.add_id_tag(3)
    assert 3 in ingredient_test.id_tags
    assert len(ingredient_test.id_tags) == 3


def test_add_id_tag_duplicate(ingredient_test):
    """Vérifie qu'un tag déjà présent n'est pas ajouté en double."""
    ingredient_test.add_id_tag(1)  # Déjà présent dans la fixture
    assert ingredient_test.id_tags.count(1) == 1


def test_remove_id_tag(ingredient_test):
    """Vérifie la suppression d'un tag existant."""
    ingredient_test.remove_id_tag(2)
    assert 2 not in ingredient_test.id_tags
    assert len(ingredient_test.id_tags) == 1


# ---------------------------
# Tests de Représentation
# ---------------------------


def test_ingredient_str(ingredient_test):
    """Vérifie l'affichage lisible de l'ingrédient."""
    # Unit.GRAM.value devrait être "g" ou "gramme" selon ton Enum
    assert "Farine" in str(ingredient_test)


def test_ingredient_repr(ingredient_test):
    """Vérifie la représentation technique pour le debug."""
    repr_str = repr(ingredient_test)
    assert "id=1" in repr_str
    assert "tags=[1, 2]" in repr_str
