from datetime import date

from src.business_objects.ingredient import Ingredient


# A modifier nom stock_item
# modifier ingredient en id_ingredient + ajout id_lot


class Lot:
    """Objet métier représentant un lot d'ingrédient spécifique.

    Attributs:
        ingredient (Ingredient): L'objet ingrédient associé au lot.
        quantity (float): Quantité disponible dans ce lot précis.
        expiry_date (date): Date de péremption du lot.
    """

    def __init__(self, ingredient: Ingredient, quantity: float, expiry_date: date):
        """Initialise une nouvelle instance de Lot avec vérifications.

        Args:
            ingredient (Ingredient): L'ingrédient contenu dans le lot.
            quantity (float): La quantité initiale du lot (doit être > 0).
            expiry_date (date): La date limite de consommation.

        Raises:
            TypeError: Si les types ne correspondent pas aux attentes.
            ValueError: Si la quantité est négative ou nulle.
        """
        if not isinstance(ingredient, Ingredient):
            raise TypeError(
                "L'argument 'ingredient' doit être une instance de la classe Ingredient."
            )

        if not isinstance(expiry_date, date):
            raise TypeError(
                "L'argument 'expiry_date' doit être une instance de datetime.date."
            )

        if not isinstance(quantity, (int, float)):
            raise TypeError("La quantité doit être un nombre (int ou float).")

        if quantity <= 0:
            raise ValueError(
                "La quantité d'un nouveau lot doit être strictement supérieure à zéro."
            )

        self.ingredient = ingredient
        self.quantity = float(quantity)
        self.expiry_date = expiry_date

    def __repr__(self):
        """Retourne une représentation textuelle destinée au debug."""
        return f"Lot(quantity={self.quantity}, unit='{self.ingredient.unit.value}', expiry_date={self.expiry_date})"
