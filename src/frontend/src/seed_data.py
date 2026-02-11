from datetime import date, timedelta

from src.backend.business_objects.ingredient import Ingredient
from src.backend.business_objects.stock import Stock
from src.backend.business_objects.unit import Unit
from src.backend.business_objects.user import Admin, GenericUser


def get_app_data():
    # 1. Utilisateurs
    users = [
        Admin(1, "Christelle", "123", id_stock=101),
        GenericUser(2, "Generic", "abc"),
    ]

    # 2. Ingrédients
    ingr_farine = Ingredient(1, "Farine", Unit.GRAM)
    ingr_lait = Ingredient(2, "Lait", Unit.LITER)
    ingr_oeufs = Ingredient(3, "Oeufs", Unit.PIECE)
    ingr_sucre = Ingredient(4, "Sucre", Unit.GRAM)
    ingr_levure = Ingredient(5, "Levure", Unit.GRAM)
    ingr_beurre = Ingredient(6, "Beurre", Unit.GRAM)
    ingr_pates = Ingredient(7, "Pates", Unit.GRAM)
    ingr_riz = Ingredient(8, "Riz", Unit.GRAM)
    ingr_tomates = Ingredient(9, "Tomates", Unit.PIECE)

    # 3. Listes des ingredients pour les stocks
    ingredients = [
        ingr_farine,
        ingr_lait,
        ingr_oeufs,
        ingr_sucre,
        ingr_levure,
        ingr_beurre,
        ingr_pates,
        ingr_riz,
        ingr_tomates,
    ]

    # 4. Stock
    stock_principal = Stock(101, "Frigo de Christelle")
    today = date.today()

    # On ajoute plusieurs lots de Lait (id=2) pour tester ton tri FEFO
    stock_principal.add_item(
        2, 502, 2.0, today + timedelta(days=15)
    )  # Lot qui périme dans 15j
    stock_principal.add_item(
        2, 505, 1.0, today + timedelta(days=5)
    )  # Lot qui périme dans 5j (sera en haut de liste)

    # On ajoute d'autres ingrédients
    stock_principal.add_item(1, 501, 1000, today + timedelta(days=30))  # Farine
    stock_principal.add_item(3, 503, 12, today + timedelta(days=20))  # Oeufs
    stock_principal.add_item(4, 504, 500, today + timedelta(days=60))  # Sucre

    # On retourne tout sous forme de dictionnaire pour le main.py
    return {
        "users": users,
        "ingredients": ingredients,
        "stocks": {stock_principal.id_stock: stock_principal},
    }
