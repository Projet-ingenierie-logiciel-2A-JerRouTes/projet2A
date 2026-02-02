from src.business_objects.unit import Unit


class Ingredient:
    """Objet métier représentant un ingrédient.

    Un ingrédient est caractérisé par :
    - un id unique,
    - un nom,
    - une unité de mesure,
    - une liste optionnelle d'identifiants de tags permettant sa catégorisation.

    Attributs:
        id_ingredient (int): Id unique de l'ingrédient.
        name (str): Nom de l'ingrédient (ex. "Farine", "Lait").
        unit (Unit): Unité de mesure associée à l'ingrédient.
        id_tags (list[int]): Liste optionnelle d'identifiants de tags.
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
            id_ingredient (int): Id de l'ingrédient.
            name (str): Nom de l'ingrédient.
            unit (Unit): Unité de mesure de l'ingrédient.
            id_tags (list[int], optionnel): Liste d'identifiants de tags.
                Par défaut, une liste vide est utilisée.

        Raises:
            ValueError: Si le nom est vide.
            TypeError: Si l'unité n'est pas une instance de Unit.
        """
        if not name:
            raise ValueError("Le nom de l'ingrédient ne peut pas être vide")

        if not isinstance(unit, Unit):
            raise TypeError("unit doit être une instance de Unit")

        self.id_ingredient = id_ingredient
        self.name = name
        self.unit = unit
        self.id_tags = id_tags if id_tags is not None else []

    def add_id_tag(self, id_tag: int):
        """Ajoute un identifiant de tag à l'ingrédient s'il n'existe pas déjà.

        Args:
            id_tag (int): Identifiant du tag à ajouter.
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
        """Retourne une représentation textuelle destinée au debug."""
        return (
            f"Ingredient(id_ingredient={self.id_ingredient}, "
            f"name='{self.name}', "
            f"unit='{self.unit.value}', "
            f"id_tags={self.id_tags})"
        )
