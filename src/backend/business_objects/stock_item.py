from datetime import date


class StockItem:
    """Objet métier représentant un lot d'ingrédient spécifique en stock.

    Attributs:
        id_ingredient (int): L'identifiant de l'ingrédient associé.
        id_lot (int): L'identifiant unique du lot.
        quantity (float): Quantité disponible dans ce lot.
        expiry_date (date): Date de péremption du lot.
    """

    def __init__(
        self, id_ingredient: int, id_lot: int, quantity: float, expiry_date: date
    ):
        """Initialise une nouvelle instance de StockItem avec vérifications."""

        # Vérifications de type
        if not isinstance(id_ingredient, int):
            raise TypeError("L'id_ingredient doit être un entier.")

        if not isinstance(id_lot, int):
            raise TypeError("L'id_lot doit être un entier.")

        if not isinstance(expiry_date, date):
            raise TypeError("L'expiry_date doit être une instance de datetime.date.")

        if not isinstance(quantity, (int, float)):
            raise TypeError("La quantité doit être un nombre.")

        # Vérification de valeur
        if quantity < 0:
            raise ValueError("La quantité ne peut pas être négative.")

        self.id_ingredient = id_ingredient
        self.id_lot = id_lot
        self.quantity = float(quantity)
        self.expiry_date = expiry_date

    def is_expired(self) -> bool:
        """Indique si le lot est périmé à la date du jour."""
        return self.expiry_date < date.today()

    def __repr__(self) -> str:
        """Représentation technique pour le debug et les listes."""
        return (
            f"StockItem(id_lot={self.id_lot}, id_ingredient={self.id_ingredient}, "
            f"quantity={self.quantity}, expiry_date={self.expiry_date})"
        )

    def __str__(self) -> str:
        """Affichage simplifié pour l'utilisateur."""
        status = "PÉRIMÉ" if self.is_expired() else "OK"
        return f"Item {self.id_lot} (Ingr: {self.id_ingredient}) : {self.quantity} [{status}]"
