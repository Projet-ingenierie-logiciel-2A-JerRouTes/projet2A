from datetime import date, timedelta
from src.backend.business_objects.user import Admin, GenericUser
from src.backend.business_objects.ingredient import Ingredient
from src.backend.business_objects.unit import Unit
from src.backend.business_objects.stock import Stock

def get_app_data():
    # 1. Ingrédients
    ingr_farine = Ingredient(1, "Farine", Unit.GRAM)
    ingr_lait = Ingredient(2, "Lait", Unit.MILLILITER)

    # 2. Stock
    stock_principal = Stock(101, "Frigo de Christelle")
    today = date.today()
    stock_principal.add_item(1, 501, 1000, today + timedelta(days=30))

    # 3. Utilisateurs
    users = [
        Admin(1, "Christelle", "123", id_stock=101),
        GenericUser(2, "Generic", "abc", id_stock=101)
    ]

    # On retourne tout sous forme de dictionnaire pour le main.py
    return {
        "users": users,
        "stocks": {stock_principal.id_stock: stock_principal}
    }
