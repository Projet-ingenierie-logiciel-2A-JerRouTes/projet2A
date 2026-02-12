from datetime import date, timedelta

from src.backend.business_objects.ingredient import Ingredient
from src.backend.business_objects.stock import Stock
from src.backend.business_objects.unit import Unit
from src.backend.business_objects.user import Admin, GenericUser


def get_app_data():
    """
    Génère l'ensemble des données de simulation.
    Cette fonction n'est appelée qu'à la demande pour éviter le chargement prématuré.
    """
    # 1. Utilisateurs (Emails corrigés pour validation Pydantic)
    users_list = [
        Admin(id_user=1, pseudo="admin", password="mdpadmin", email="admin@admin.com"),
        GenericUser(
            id_user=2,
            pseudo="user1",
            password="mdpuser1",
            email="user1@example.com",
            id_stock=101,
        ),
    ]

    # 2. Catalogue d'Ingrédients
    ingredients = [
        Ingredient(1, "Farine", Unit.GRAM),
        Ingredient(2, "Lait", Unit.LITER),
        Ingredient(3, "Oeufs", Unit.PIECE),
        Ingredient(4, "Sucre", Unit.GRAM),
        Ingredient(5, "Levure", Unit.GRAM),
        Ingredient(6, "Beurre", Unit.GRAM),
        Ingredient(7, "Pates", Unit.GRAM),
        Ingredient(8, "Riz", Unit.GRAM),
        Ingredient(9, "Tomates", Unit.PIECE),
    ]

    # 3. Stock principal (ID 101 pour correspondre au GenericUser)
    stock_principal = Stock(101, "Frigo de Christelle")
    today = date.today()

    # Ajout d'items avec gestion FEFO (First Expired, First Out)
    stock_principal.add_item(2, 502, 2.0, today + timedelta(days=15))  # Lait lot 1
    stock_principal.add_item(
        2, 505, 1.0, today + timedelta(days=5)
    )  # Lait lot 2 (périme avant)
    stock_principal.add_item(1, 501, 1000, today + timedelta(days=30))  # Farine
    stock_principal.add_item(3, 503, 12, today + timedelta(days=20))  # Oeufs
    stock_principal.add_item(4, 504, 500, today + timedelta(days=60))  # Sucre

    return {
        "users": users_list,
        "ingredients": ingredients,
        "stocks": {stock_principal.id_stock: stock_principal},
    }


# --- GESTION DU CACHE (SINGLETON PARESSEUX) ---
_cached_data = None


def get_demo_data():
    """
    Point d'entrée unique pour récupérer les données de démo.
    L'exécution se fait ici uniquement au premier appel.
    """
    global _cached_data
    if _cached_data is None:
        # Les logs d'initialisation n'apparaîtront qu'ici
        print("🚀 [SEED] Initialisation paresseuse des données de démo...")
        _cached_data = get_app_data()
    return _cached_data
