class Stock:
    """
    Classe représentant le stock d'un utilisateur.

    Attributs :
        ingredients (dict) : clé = nom de l'ingrédient, valeur = quantité disponible
    """

    def __init__(self):
        # Stock initial vide
        self.ingredients: dict[str, float] = {}

    # -------------------------------------------------
    # Méthodes de gestion du stock
    # -------------------------------------------------

    def add_ingredient(self, name: str, quantity: float):
        """Ajoute un ingrédient au stock ou augmente sa quantité si déjà présent."""
        if name in self.ingredients:
            self.ingredients[name] += quantity
        else:
            self.ingredients[name] = quantity
        print(f"{quantity} {name} ajouté(s). Nouveau total : {self.ingredients[name]}")

    def remove_ingredient(self, name: str, quantity: float):
        """Retire une quantité d'ingrédient. Supprime l'ingrédient si la quantité tombe à 0."""
        if name not in self.ingredients:
            print(f"{name} n'est pas présent dans le stock.")
            return

        if quantity >= self.ingredients[name]:
            del self.ingredients[name]
            print(f"{name} supprimé du stock.")
        else:
            self.ingredients[name] -= quantity
            print(
                f"{quantity} {name} retiré(s). Nouveau total : {self.ingredients[name]}"
            )

    def update_quantity(self, name: str, quantity: float):
        """Met à jour la quantité d'un ingrédient, ajoute s'il n'existe pas."""
        self.ingredients[name] = quantity
        print(f"Quantité de {name} mise à jour à {quantity}.")

    def has_ingredient(self, name: str, quantity: float) -> bool:
        """Vérifie si le stock contient au moins la quantité demandée."""
        return self.ingredients.get(name, 0) >= quantity

    def list_ingredients(self):
        """Affiche tous les ingrédients et leurs quantités."""
        for name, qty in self.ingredients.items():
            print(f"{name}: {qty}")
