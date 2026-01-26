from src.business_objects.unit import Unit


class Ingredient:
    """Objet métier représentant un ingrédient.

    Un ingrédient est caractérisé par :
    - un nom,
    - une unité de mesure,
    - une liste optionnelle de tags permettant sa catégorisation.


    Attributs:
        name (str): Nom de l'ingrédient (ex. "Farine", "Lait").
        unit (Unit): Unité de mesure associée à l'ingrédient.
        tags (list[str]): Liste optionnelle de tags décrivant
            l'ingrédient (ex. "bio", "sec", "frais").
    """

    def __init__(self, name: str, unit: Unit, tags=None):
        """Initialise une nouvelle instance d'Ingredient.

        Args:
            name (str): Nom de l'ingrédient.
            unit (Unit): Unité de mesure de l'ingrédient.
            tags (list[str], optionnel): Liste de tags associés à
                l'ingrédient. Par défaut, une liste vide est utilisée.

        Raises:
            ValueError: Si le nom est vide.
            TypeError: Si l'unité n'est pas une instance de Unit.
        """
        if not name:
            raise ValueError("Le nom de l'ingrédient ne peut pas être vide")

        if not isinstance(unit, Unit):
            raise TypeError("unit doit être une instance de Unit")

        self.name = name
        self.unit = unit
        self.tags = tags if tags is not None else []

    def add_tag(self, tag: str):
        """Ajoute un tag à l'ingrédient s'il n'existe pas déjà.

        Args:
            tag (str): Tag à ajouter.
        """

        tag = tag.lower()
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """Supprime un tag de l'ingrédient s'il est présent.

        Args:
            tag (str): Tag à supprimer.
        """

        tag = tag.lower()
        if tag in self.tags:
            self.tags.remove(tag)

    def __repr__(self):
        """Retourne une représentation textuelle destinée au debug."""
        return (
            f"Ingredient(name='{self.name}', "
            f"unit='{self.unit.value}', "
            f"tags={self.tags})"
        )
