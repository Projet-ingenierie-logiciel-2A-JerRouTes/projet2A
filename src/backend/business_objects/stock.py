from collections import defaultdict
from datetime import date

from src.backend.business_objects.stockItem import StockItem


class Stock:
    """Gestionnaire de l'inventaire des ingrédients (Entrepôt).

    Attributs:
        id_stock (int): Identifiant unique du stock (ex: Stock Central, Stock Cuisine).
        nom (str): Nom du stock.
        items_by_ingredient (dict[int, list[StockItem]]): Dictionnaire indexé par id_ingredient.
    """

    def __init__(self, id_stock: int, nom: str):
        """Initialise un stock avec un nom et un ID."""
        self.id_stock = id_stock
        self.nom = nom
        # On indexe par id_ingredient pour plus de cohérence avec la BDD
        self.items_by_ingredient = defaultdict(list)

    # -------------------------------------------------
    # Méthodes de gestion du stock
    # -------------------------------------------------

    def add_item(
        self, id_ingredient: int, id_lot: int, quantity: float, expiry_date: date
    ):
        """Crée et ajoute un StockItem au stock, puis trie par date de péremption (FEFO)."""

        # On délègue la validation au constructeur de StockItem
        new_item = StockItem(id_ingredient, id_lot, quantity, expiry_date)

        self.items_by_ingredient[id_ingredient].append(new_item)
        # Tri automatique pour que le prochain lot à périmer soit toujours à l'index 0
        self.items_by_ingredient[id_ingredient].sort(key=lambda x: x.expiry_date)

        print(
            f"Ajout au stock '{self.nom}': {quantity} de l'ingrédient {id_ingredient}."
        )

    def get_total_quantity(self, id_ingredient: int) -> float:
        """Calcule la quantité totale disponible pour un ingrédient (tous lots confondus)."""
        return sum(
            item.quantity for item in self.items_by_ingredient.get(id_ingredient, [])
        )

    def remove_quantity(self, id_ingredient: int, quantity_to_consume: float):
        """Consomme la quantité demandée en suivant la méthode FEFO."""

        if quantity_to_consume <= 0:
            raise ValueError("La quantité à consommer doit être strictement positive.")

        total_available = self.get_total_quantity(id_ingredient)

        if quantity_to_consume > total_available:
            raise ValueError(
                f"Stock insuffisant (Ingrédient {id_ingredient}) : "
                f"demande {quantity_to_consume}, disponible {total_available}."
            )

        items = self.items_by_ingredient[id_ingredient]

        # Logique de consommation FEFO
        while quantity_to_consume > 0 and items:
            current_item = items[0]

            if current_item.quantity > quantity_to_consume:
                current_item.quantity -= quantity_to_consume
                quantity_to_consume = 0
            else:
                quantity_to_consume -= current_item.quantity
                items.pop(0)  # Le lot est vide, on le retire du stock

    def __repr__(self) -> str:
        return f"Stock(id={self.id_stock}, nom='{self.nom}', nb_ingredients={len(self.items_by_ingredient)})"
