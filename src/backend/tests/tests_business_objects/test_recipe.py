import pytest
from src.backend.business_objects.recipe import Recipe
from src.backend.business_objects.user import GenericUser


# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def recipe_test():
    """Retourne une recette de base pour les tests."""
    creator = GenericUser(id_user=10, pseudo="lucie", password="____")
    r = Recipe(recipe_id=1, creator=creator, status="draft", prep_time=30, portions=4)
    r.add_translation("fr", "Crêpes", "Recette traditionnelle")
    r.add_ingredient(ingredient_id=101, quantity=500.0)  # Farine
    r.add_ingredient(ingredient_id=102, quantity=4.0)  # Œufs
    return r


# ---------------------------
# Tests d'Initialisation
# ---------------------------


def test_recipe_initialization_success(recipe_test):
    """Vérifie que la recette est créée avec les bonnes valeurs."""
    assert recipe_test.recipe_id == 1
    assert recipe_test.status == "draft"
    assert recipe_test.portions == 4
    assert len(recipe_test.ingredients) == 2
    assert recipe_test.creator.id_user == 10


def test_recipe_invalid_portions():
    """Vérifie qu'une erreur est levée pour un nombre de portions invalide."""
    creator = GenericUser(id_user=10, pseudo="lucie", password="____")
    with pytest.raises(
        ValueError, match="Le nombre de portions doit être supérieur à zéro"
    ):
        Recipe(recipe_id=2, creator=creator, status="draft", prep_time=15, portions=0)


# ---------------------------
# Tests de Gestion du Statut
# ---------------------------


def test_changer_statut(recipe_test):
    """Vérifie la mise à jour du statut."""
    recipe_test.changer_statut("public")
    assert recipe_test.status == "public"
    # Vérification visuelle via print_status (optionnel dans un test auto)
    recipe_test.print_status()


# ---------------------------
# Tests de Scaling (Portions)
# ---------------------------


def test_scale_portions_up(recipe_test):
    """Vérifie que les quantités doublent quand on passe de 4 à 8 portions."""
    recipe_test.scale_portions(8)

    assert recipe_test.portions == 8
    # Ingrédient 101 : 500 * (8/4) = 1000
    assert recipe_test.ingredients[0][1] == 1000.0
    # Ingrédient 102 : 4 * (8/4) = 8
    assert recipe_test.ingredients[1][1] == 8.0


def test_scale_portions_down(recipe_test):
    """Vérifie que les quantités diminuent de moitié quand on passe de 4 à 2 portions."""
    recipe_test.scale_portions(2)

    assert recipe_test.portions == 2
    # Ingrédient 101 : 500 * (2/4) = 250
    assert recipe_test.ingredients[0][1] == 250.0
    # Ingrédient 102 : 4 * (2/4) = 2
    assert recipe_test.ingredients[1][1] == 2.0
