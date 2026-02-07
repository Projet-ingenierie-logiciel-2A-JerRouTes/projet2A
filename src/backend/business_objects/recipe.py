class Recipe:
    """
    Représente une recette de cuisine.

    Cette classe modélise la logique métier d'une recette, indépendamment
    de la persistance. Elle gère les caractéristiques de base (portions, temps),
    les ingrédients associés, ainsi que les traductions en plusieurs langues.
    """

    def __init__(
        self,
        recipe_id: int,
        creator_id: int,
        status: str,
        prep_time: int,
        portions: int,
    ):
        """
        Initialise une instance de Recipe avec validations.

        Args:
            recipe_id (int): Identifiant unique de la recette.
            creator_id (int): Identifiant de l'utilisateur créateur.
            status (str): Statut initial (ex: 'draft', 'public').
            prep_time (int): Temps de préparation en minutes.
            portions (int): Nombre de portions (doit être > 0).

        Raises:
            ValueError: Si le nombre de portions est inférieur ou égal à zéro.
        """
        if portions <= 0:
            raise ValueError("Le nombre de portions doit être supérieur à zéro.")

        # --- Attributs de base ---
        self._recipe_id = recipe_id
        self._creator_id = creator_id
        self.status = status
        self.prep_time = prep_time
        self.portions = portions

        # --- Relations ---
        self.ingredients = []  # Liste de tuples (id_ingredient, quantite)
        self.tags = []
        self.translations = {}

    @property
    def recipe_id(self) -> int:
        """Retourne l'identifiant BDD de la recette (lecture seule)."""
        return self._recipe_id

    # -------------------------------------------------
    # Méthodes de gestion
    # -------------------------------------------------

    def add_ingredient(self, ingredient_id: int, quantity: float):
        """
        Ajoute un ingrédient à la recette.

        Args:
            ingredient_id (int): Identifiant de l'ingrédient.
            quantity (float): Quantité requise (doit être positive).

        Raises:
            ValueError: Si la quantité est négative ou nulle.
        """
        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")
        self.ingredients.append((ingredient_id, quantity))

    def add_translation(self, language_code: str, name: str, description: str):
        """
        Ajoute ou met à jour une traduction pour la recette.

        Args:
            language_code (str): Code langue ISO (ex: 'fr', 'en').
            name (str): Nom localisé de la recette.
            description (str): Description localisée.
        """
        self.translations[language_code] = {
            "name": name,
            "description": description,
        }

    def changer_statut(self, new_status: str):
        """
        Modifie le statut de la recette.

        Args:
            new_status (str): Nouveau statut à appliquer.
        """
        self.status = new_status
        print(f"Statut de la recette {self._recipe_id} mis à jour : {self.status}")

    def print_status(self):
        """Affiche le statut actuel dans la console."""
        print(f"Le statut actuel est : {self.status}")

    def scale_portions(self, new_portions: int):
        """
        Adapte les quantités d'ingrédients pour un nouveau nombre de portions.

        Args:
            new_portions (int): Nouveau nombre de portions souhaité.
        """
        if new_portions <= 0:
            return
        factor = new_portions / self.portions
        self.ingredients = [(i_id, q * factor) for i_id, q in self.ingredients]
        self.portions = new_portions

    # -------------------------------------------------
    # Méthodes d'affichage
    # -------------------------------------------------

    def afficher_recette(self, lang: str = "fr"):
        """
        Affiche les détails complets de la recette dans la console.

        Args:
            lang (str, optional): Code langue pour l'affichage.
                Défaut: "fr".
        """
        trans = self.translations.get(lang, self.translations.get("en", {}))
        name = trans.get("name", "Nom inconnu")

        print(f"--- {name.upper()} ---")
        print(f"Portions: {self.portions} | Temps: {self.prep_time} min")
        print(f"Statut: {self.status}")
        print("Ingrédients (ID | Quantité) :")
        for i_id, q in self.ingredients:
            print(f" - {i_id} : {q:.2f}")

    def __str__(self) -> str:
        """
        Retourne une représentation lisible de la recette.

        Returns:
            str: Nom traduit de la recette ou identifiant si absent.
        """
        name = self.translations.get("fr", {}).get("name", f"Recette {self._recipe_id}")
        return f"[Recipe {self._recipe_id}] {name} ({self.status})"

    def __repr__(self) -> str:
        """
        Retourne une représentation technique destinée au debug.

        Returns:
            str: Représentation technique de l'objet Recipe.
        """
        return (
            f"Recipe(id={self._recipe_id}, "
            f"status='{self.status}', "
            f"portions={self.portions})"
        )
