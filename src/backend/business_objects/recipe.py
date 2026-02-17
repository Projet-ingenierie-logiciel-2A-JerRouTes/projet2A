from src.backend.business_objects.user import User


class Recipe:
    """
    Représente une recette de cuisine.

    Classe métier: elle ne dépend pas de la BDD.
    Une recette a un créateur (objet User), pas un creator_id (clé étrangère).
    """

    def __init__(
        self,
        recipe_id: int,
        creator: User,
        status: str,
        prep_time: int,
        portions: int,
    ):
        """
        Args:
            recipe_id (int): Identifiant unique de la recette.
            creator (User): Utilisateur créateur (objet métier).
            status (str): Statut initial (ex: 'draft', 'public').
            prep_time (int): Temps de préparation en minutes.
            portions (int): Nombre de portions (doit être > 0).
        """
        if portions <= 0:
            raise ValueError("Le nombre de portions doit être supérieur à zéro.")

        self._recipe_id = recipe_id
        self.creator = creator  # objet métier
        self.status = status
        self.prep_time = prep_time
        self.portions = portions

        self.ingredients = []  # Liste de tuples (id_ingredient, quantite)
        self.tags = []
        self.translations = {}

    @property
    def recipe_id(self) -> int:
        return self._recipe_id

    @property
    def creator_id(self) -> int:
        """
        Alias pratique (souvent utile côté API/DAO) :
        permet de récupérer l'id sans stocker un champ BDD dans l'objet métier.
        """
        return self.creator.id_user

    # -------------------------------------------------
    # Méthodes de gestion
    # -------------------------------------------------

    def add_ingredient(self, ingredient_id: int, quantity: float):
        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")
        self.ingredients.append((ingredient_id, quantity))

    def add_translation(self, language_code: str, name: str, description: str):
        self.translations[language_code] = {"name": name, "description": description}

    def changer_statut(self, new_status: str):
        self.status = new_status
        print(f"Statut de la recette {self._recipe_id} mis à jour : {self.status}")

    def print_status(self):
        print(f"Le statut actuel est : {self.status}")

    def scale_portions(self, new_portions: int):
        if new_portions <= 0:
            return
        factor = new_portions / self.portions
        self.ingredients = [(i_id, q * factor) for i_id, q in self.ingredients]
        self.portions = new_portions

    # -------------------------------------------------
    # Méthodes d'affichage
    # -------------------------------------------------

    def afficher_recette(self, lang: str = "fr"):
        trans = self.translations.get(lang, self.translations.get("en", {}))
        name = trans.get("name", "Nom inconnu")

        print(f"--- {name.upper()} ---")
        print(f"Créateur: {self.creator.username} (ID: {self.creator_id})")
        print(f"Portions: {self.portions} | Temps: {self.prep_time} min")
        print(f"Statut: {self.status}")
        print("Ingrédients (ID | Quantité) :")
        for i_id, q in self.ingredients:
            print(f" - {i_id} : {q:.2f}")

    def __str__(self) -> str:
        name = self.translations.get("fr", {}).get("name", f"Recette {self._recipe_id}")
        return f"[Recipe {self._recipe_id}] {name} ({self.status})"

    def __repr__(self) -> str:
        return (
            f"Recipe(id={self._recipe_id}, "
            f"creator_id={self.creator_id}, "
            f"status='{self.status}', "
            f"portions={self.portions})"
        )
