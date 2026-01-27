from collections import defaultdict
from datetime import date

from src.business_objects.ingredient import Ingredient
from src.business_objects.lot import Lot


class Stock:
    """Gestionnaire de l'inventaire des ingrédients.

    Attributs:
        ingredients_by_name (dict[str, list[Lot]]): Dictionnaire trié par date de péremption.
    """

    def __init__(self):
        """Initialise un stock vide."""
        self.ingredients_by_name: dict[str, list[Lot]] = defaultdict(list)

    # -------------------------------------------------
    # Méthodes de gestion du stock
    # -------------------------------------------------

    def add_ingredient(
        self, ingredient: Ingredient, quantity: float, expiry_date: date
    ):
        """Ajoute un nouveau lot au stock après validation des données.

        Args:
            ingredient (Ingredient): L'ingrédient à ajouter.
            quantity (float): La quantité à intégrer.
            expiry_date (date): La date de péremption du lot.

        Raises:
            TypeError ou ValueError: Si les données du lot sont invalides.
        """
        # La validation est déléguée au constructeur de Lot
        new_lot = Lot(ingredient, quantity, expiry_date)

        self.ingredients_by_name[ingredient.name].append(new_lot)
        self.ingredients_by_name[ingredient.name].sort(key=lambda x: x.expiry_date)

    def get_total_quantity(self, name: str) -> float:
        """Calcule la quantité totale disponible pour un ingrédient donné.

        Args:
            name (str): Nom de l'ingrédient.

        Returns:
            float: La somme des quantités.
        """
        if not isinstance(name, str):
            raise TypeError(
                "Le nom de l'ingrédient doit être une chaîne de caractères."
            )

        return sum(lot.quantity for lot in self.ingredients_by_name.get(name, []))

    def remove_quantity(self, name: str, quantity_to_consume: float):
        """Consomme une quantité d'ingrédient selon la méthode FEFO.

        Args:
            name (str): Nom de l'ingrédient à retirer.
            quantity_to_consume (float): Quantité à déduire (doit être > 0).

        Raises:
            TypeError: Si la quantité n'est pas un nombre.
            ValueError: Si la quantité est <= 0 ou si le stock est insuffisant.
        """
        if not isinstance(quantity_to_consume, (int, float)):
            raise TypeError("La quantité à consommer doit être un nombre.")

        if quantity_to_consume <= 0:
            raise ValueError("La quantité à consommer doit être strictement positive.")

        total_available = self.get_total_quantity(name)

        if quantity_to_consume > total_available:
            raise ValueError(
                f"Stock insuffisant pour {name} : demande {quantity_to_consume}, disponible {total_available}."
            )

        lots = self.ingredients_by_name[name]

        while quantity_to_consume > 0 and lots:
            current_lot = lots[0]

            if current_lot.quantity > quantity_to_consume:
                current_lot.quantity -= quantity_to_consume
                quantity_to_consume = 0
            else:
                quantity_to_consume -= current_lot.quantity
                lots.pop(0)

    # -------------------------------------------------
    # Méthodes de recherche de recette
    # -------------------------------------------------
