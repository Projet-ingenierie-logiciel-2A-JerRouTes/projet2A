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
        Admin(
            id_user=1,
            pseudo="admin",
            password="mdpadmin",
            email="admin@admin.com",
            id_stock=[101, 102],
        ),
        GenericUser(
            id_user=2,
            pseudo="user1",
            password="mdpuser1",
            email="user1@example.com",
            id_stock=103,
        ),
    ]

    # 2. Catalogue d'Ingrédients
    ingredients = {
        1: Ingredient(1, "Farine", Unit.GRAM),
        2: Ingredient(2, "Lait", Unit.LITER),
        3: Ingredient(3, "Oeufs", Unit.PIECE),
        4: Ingredient(4, "Sucre", Unit.GRAM),
        5: Ingredient(5, "Levure", Unit.GRAM),
        6: Ingredient(6, "Beurre", Unit.GRAM),
        7: Ingredient(7, "Pates", Unit.GRAM),
        8: Ingredient(8, "Riz", Unit.GRAM),
        9: Ingredient(9, "Tomates", Unit.PIECE),
    }

    # 3. Stock principal (ID 101 pour correspondre au GenericUser)
    stock_1 = Stock(101, "Frigo Admin")
    stock_2 = Stock(102, "Placard Admin")

    stock_3 = Stock(103, "Stock vide")  # Stock vide pour l'autre utilisateur
    today = date.today()

    # Ajout d'items avec gestion FEFO (First Expired, First Out)
    stock_1.add_item(2, 502, 5.0, today + timedelta(days=15))  # Lait lot 1
    stock_1.add_item(
        2, 505, 1.0, today + timedelta(days=5)
    )  # Lait lot 2 (périme avant)
    stock_1.add_item(6, 501, 500, today + timedelta(days=30))  # Beurre

    stock_2.add_item(3, 601, 12, today + timedelta(days=20))  # Oeufs
    stock_2.add_item(4, 602, 500, today + timedelta(days=60))  # Sucre
    stock_2.add_item(1, 603, 1000, today + timedelta(days=90))  # Farine

    return {
        "users": users_list,
        "ingredients": ingredients,
        "stocks": {
            stock_1.id_stock: stock_1,
            stock_2.id_stock: stock_2,
            stock_3.id_stock: stock_3,
        },
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
