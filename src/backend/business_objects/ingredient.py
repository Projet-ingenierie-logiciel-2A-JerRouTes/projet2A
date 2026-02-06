from src.backend.business_objects.unit import Unit


class Ingredient:
    """
    Représente un ingrédient de base utilisé dans les recettes.

    Cette classe définit les propriétés fondamentales d'un produit (nom, unité)
    et gère sa catégorisation via un système d'identifiants de tags.
    """

    def __init__(
        self,
        id_ingredient: int,
        name: str,
        unit: Unit,
        id_tags: list[int] | None = None,
    ):
        """
        Initialise une instance d'Ingredient avec validations de type.

        :param id_ingredient: Identifiant unique de l'ingrédient
        :param name: Nom de l'ingrédient (ex: "Farine")
        :param unit: Unité de mesure (instance de l'Enum Unit)
        :param id_tags: Liste d'identifiants de tags (optionnel)

        :raises ValueError: Si le nom est vide
        :raises TypeError: Si l'unité n'est pas une instance de Unit
        """
        if not name or name.strip() == "":
            raise ValueError("Le nom de l'ingrédient ne peut pas être vide.")

        if not isinstance(unit, Unit):
            raise TypeError("L'argument 'unit' doit être une instance de Unit.")

        # --- Attributs ---
        self._id_ingredient = id_ingredient
        self.name = name
        self.unit = unit
        self.id_tags = id_tags if id_tags is not None else []

    @property
    def id_ingredient(self) -> int:
        """L'identifiant BDD est en lecture seule."""
        return self._id_ingredient

    # -------------------------------------------------
    # Méthodes de gestion
    # -------------------------------------------------

    def add_id_tag(self, id_tag: int):
        """
        Ajoute un identifiant de tag à l'ingrédient s'il n'existe pas déjà.

        :param id_tag: Identifiant du tag à ajouter
        :raises TypeError: Si id_tag n'est pas un entier
        """
        if not isinstance(id_tag, int):
            raise TypeError("id_tag doit être un entier.")

        if id_tag not in self.id_tags:
            self.id_tags.append(id_tag)

    def remove_id_tag(self, id_tag: int):
        """
        Supprime un identifiant de tag de l'ingrédient.

        :param id_tag: Identifiant du tag à supprimer
        """
        if id_tag in self.id_tags:
            self.id_tags.remove(id_tag)

    # -------------------------------------------------
    # Méthodes d'affichage
    # -------------------------------------------------

    def __str__(self) -> str:
        """
        Retourne une représentation lisible de l'ingrédient.
        """
        return f"{self.name} (Unité: {self.unit.value})"

    def __repr__(self) -> str:
        """
        Retourne une représentation technique destinée au debug.
        """
        return (
            f"Ingredient(id={self._id_ingredient}, name='{self.name}', "
            f"unit='{self.unit.value}', tags={self.id_tags})"
        )
