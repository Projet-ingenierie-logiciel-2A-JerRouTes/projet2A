from business_objects.unit import Unit


class Ingredient:
    """Objet métier représentant un ingrédient.

    Un ingrédient est défini par :
    - un identifiant unique,
    - un nom,
    - une unité de mesure,
    - une liste optionnelle d'identifiants de tags.

    Attributes:
        id_ingredient (int): Identifiant unique de l'ingrédient.
        name (str): Nom de l'ingrédient (ex: "Farine", "Lait").
        unit (Unit): Unité de mesure associée à l'ingrédient.
        id_tags (list[int]): Liste des identifiants de tags associés.
    """

    def __init__(
        self,
        id_ingredient: int,
        name: str,
        unit: Unit,
        id_tags: list[int] | None = None,
    ):
        """Initialise une nouvelle instance d'Ingredient.

        Args:
            id_ingredient (int): Identifiant de l'ingrédient.
            name (str): Nom de l'ingrédient.
            unit (Unit): Unité de mesure de l'ingrédient.
            id_tags (list[int] | None): Liste optionnelle d'identifiants de tags.
                Si None, une liste vide est créée.

        Raises:
            ValueError: Si le nom de l'ingrédient est vide.
            TypeError: Si l'unité n'est pas une instance de Unit.
        """
        if not name:
            raise ValueError("Le nom de l'ingrédient ne peut pas être vide")

        if not isinstance(unit, Unit):
            raise TypeError("L'argument 'unit' doit être une instance de Unit")

        self.id_ingredient = id_ingredient
        self.name = name
        self.unit = unit
        self.id_tags = id_tags if id_tags is not None else []

    def add_id_tag(self, id_tag: int):
        """Ajoute un identifiant de tag à l'ingrédient s'il n'existe pas déjà.

        Args:
            id_tag (int): Identifiant du tag à ajouter.

        Raises:
            TypeError: Si l'identifiant du tag n'est pas un entier.
        """
        if not isinstance(id_tag, int):
            raise TypeError("id_tag doit être un entier")

        if id_tag not in self.id_tags:
            self.id_tags.append(id_tag)

    def remove_id_tag(self, id_tag: int):
        """Supprime un identifiant de tag de l'ingrédient s'il est présent.

        Args:
            id_tag (int): Identifiant du tag à supprimer.
        """
        if id_tag in self.id_tags:
            self.id_tags.remove(id_tag)

    def __repr__(self):
        """Retourne une représentation textuelle de l'ingrédient pour le debug.

        Returns:
            str: Représentation technique de l'ingrédient.
        """
        return (
            f"Ingredient(id={self.id_ingredient}, "
            f"name='{self.name}', "
            f"unit='{self.unit.value}', "
            f"tags={self.id_tags})"
        )
