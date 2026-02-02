from enum import Enum


class Unit(Enum):
    """Enumération des unités de mesure pour les ingrédients.

    Cette énumération définit l'ensemble des unités autorisées
    dans le domaine métier.
    """

    GRAM = "g"
    KILOGRAM = "kg"
    MILIGRAM = "mg"
    MILLILITER = "ml"
    LITER = "L"
    CENTIMETER = "cm"
    PIECE = "pcs"
