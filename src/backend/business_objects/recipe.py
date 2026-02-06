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

        :param recipe_id: Identifiant unique de la recette
        :param creator_id: Identifiant de l'utilisateur créateur
        :param status: Statut initial (ex: 'draft', 'public')
        :param prep_time: Temps de préparation en minutes
        :param portions: Nombre de portions (doit être > 0)

        :raises ValueError: Si le nombre de portions est inférieur ou égal à zéro
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
        """L'identifiant BDD est en lecture seule."""
        return self._recipe_id

    # -------------------------------------------------
    # Méthodes de gestion
    # -------------------------------------------------

    def add_ingredient(self, ingredient_id: int, quantity: float):
        """
        Ajoute un ingrédient à la recette.

        :param ingredient_id: Identifiant de l'ingrédient
        :param quantity: Quantité requise (doit être positive)
        :raises ValueError: Si la quantité est négative ou nulle
        """
        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")
        self.ingredients.append((ingredient_id, quantity))

    def add_translation(self, language_code: str, name: str, description: str):
        """
        Ajoute ou met à jour une traduction pour la recette.

        :param language_code: Code langue ISO (ex: 'fr', 'en')
        :param name: Nom localisé de la recette
        :param description: Description localisée
        """
        self.translations[language_code] = {"name": name, "description": description}

    def changer_statut(self, new_status: str):
        """
        Modifie le statut de la recette.

        :param new_status: Nouveau statut à appliquer
        """
        self.status = new_status
        print(f"Statut de la recette {self._recipe_id} mis à jour : {self.status}")

    def print_status(self):
        """
        Affiche le statut actuel dans la console.
        """
        print(f"Le statut actuel est : {self.status}")

    def scale_portions(self, new_portions: int):
        """
        Adapte les quantités d'ingrédients pour un nouveau nombre de portions.

        :param new_portions: Nouveau nombre de portions souhaité
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

        :param lang: Code langue pour l'affichage (défaut: 'fr')
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
        Retourne une représentation lisible (nom traduit ou ID).
        """
        name = self.translations.get("fr", {}).get("name", f"Recette {self._recipe_id}")
        return f"[Recipe {self._recipe_id}] {name} ({self.status})"

    def __repr__(self) -> str:
        """
        Retourne une représentation technique destinée au debug.
        """
        return f"Recipe(id={self._recipe_id}, status='{self.status}', portions={self.portions})"
