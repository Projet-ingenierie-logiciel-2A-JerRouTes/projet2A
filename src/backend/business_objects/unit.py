from __future__ import annotations

from enum import Enum
from typing import Any


class Unit(Enum):
    """Enumération des unités de mesure (valeurs canoniques stockables en DB).

    Notes:
        - La valeur de chaque Enum est la représentation canonique stockée en base.
        - Utilise `Unit.from_any()` pour parser des entrées utilisateur variées
          (anglais/français, pluriels, symboles).
        - Utilise `convert_to()` pour convertir entre unités compatibles.
    """

    # Masse
    GRAM = "g"
    KILOGRAM = "kg"
    MILLIGRAM = "mg"
    OUNCE = "oz"  # masse (avoirpois)
    POUND = "lb"

    # Volume
    MILLILITER = "ml"
    LITER = "L"
    FLUID_OUNCE = "fl_oz"  # volume (US fl oz)

    # Longueur
    CENTIMETER = "cm"
    METER = "m"

    # Compte
    PIECE = "pcs"

    # -------------------------------
    # Catégorisation (compatibilité)
    # -------------------------------
    @property
    def category(self) -> str:
        """Retourne la catégorie de l’unité (mass, volume, length, count)."""
        if self in {Unit.GRAM, Unit.KILOGRAM, Unit.MILLIGRAM, Unit.OUNCE, Unit.POUND}:
            return "mass"
        if self in {Unit.MILLILITER, Unit.LITER, Unit.FLUID_OUNCE}:
            return "volume"
        if self in {Unit.CENTIMETER, Unit.METER}:
            return "length"
        return "count"

    # -------------------------------
    # Parsing / normalisation
    # -------------------------------
    @classmethod
    def from_any(cls, raw: Any) -> Unit:
        """Normalise une entrée en `Unit`.

        Args:
            raw: Entrée brute (Unit, str, etc.). Exemples acceptés:
                - "g", "gram", "grams", "gramme", "grammes"
                - "kg", "kilogram", "kilogramme"
                - "ml", "milliliter", "millilitre", "mL"
                - "l", "L", "liter", "litre"
                - "oz", "ounce", "once"
                - "fl oz", "floz", "fluid ounce"
                - "pcs", "pc", "piece", "pièce", "pieces", "pièces"
                - "cm", "centimeter", "centimètre"

        Returns:
            Unit: Unité canonique correspondante.

        Raises:
            ValueError: Si l’entrée ne correspond à aucune unité connue.
        """
        if isinstance(raw, Unit):
            return raw

        if raw is None:
            raise ValueError("Unit.from_any(): raw is None")

        s = str(raw).strip().lower()

        # Normalisation légère: espaces, points, pluriels simples
        s = s.replace(".", "").replace(",", "").strip()
        s = " ".join(s.split())  # collapse spaces

        aliases = {
            # Masse
            "g": cls.GRAM,
            "gram": cls.GRAM,
            "grams": cls.GRAM,
            "gramme": cls.GRAM,
            "grammes": cls.GRAM,
            "kg": cls.KILOGRAM,
            "kilogram": cls.KILOGRAM,
            "kilograms": cls.KILOGRAM,
            "kilogramme": cls.KILOGRAM,
            "kilogrammes": cls.KILOGRAM,
            "mg": cls.MILLIGRAM,
            "milligram": cls.MILLIGRAM,
            "milligrams": cls.MILLIGRAM,
            "milligramme": cls.MILLIGRAM,
            "milligrammes": cls.MILLIGRAM,
            "oz": cls.OUNCE,
            "ounce": cls.OUNCE,
            "ounces": cls.OUNCE,
            "once": cls.OUNCE,  # FR fréquent
            "lb": cls.POUND,
            "lbs": cls.POUND,
            "pound": cls.POUND,
            "pounds": cls.POUND,
            "livre": cls.POUND,
            "livres": cls.POUND,
            # Volume
            "ml": cls.MILLILITER,
            "mL".lower(): cls.MILLILITER,
            "milliliter": cls.MILLILITER,
            "milliliters": cls.MILLILITER,
            "millilitre": cls.MILLILITER,
            "millilitres": cls.MILLILITER,
            "l": cls.LITER,
            "L".lower(): cls.LITER,
            "liter": cls.LITER,
            "liters": cls.LITER,
            "litre": cls.LITER,
            "litres": cls.LITER,
            "fl oz": cls.FLUID_OUNCE,
            "floz": cls.FLUID_OUNCE,
            "fluid ounce": cls.FLUID_OUNCE,
            "fluid ounces": cls.FLUID_OUNCE,
            "fl_oz": cls.FLUID_OUNCE,
            "fl-oz": cls.FLUID_OUNCE,
            # Longueur
            "cm": cls.CENTIMETER,
            "centimeter": cls.CENTIMETER,
            "centimeters": cls.CENTIMETER,
            "centimetre": cls.CENTIMETER,
            "centimetres": cls.CENTIMETER,
            "centimètre": cls.CENTIMETER,
            "centimètres": cls.CENTIMETER,
            "m": cls.METER,
            "meter": cls.METER,
            "meters": cls.METER,
            "metre": cls.METER,
            "metres": cls.METER,
            "mètre": cls.METER,
            "mètres": cls.METER,
            # Compte
            "pcs": cls.PIECE,
            "pc": cls.PIECE,
            "piece": cls.PIECE,
            "pieces": cls.PIECE,
            "pièce": cls.PIECE,
            "pièces": cls.PIECE,
            "unite": cls.PIECE,
            "unité": cls.PIECE,
            "unit": cls.PIECE,
            "units": cls.PIECE,
        }

        if s in aliases:
            return aliases[s]

        # fallback: tentative directe sur les valeurs canoniques
        for u in cls:
            if u.value.lower() == s:
                return u

        raise ValueError(f"Unité inconnue: {raw!r}")

    # -------------------------------
    # Conversion (optionnel mais utile)
    # -------------------------------
    def convert_to(self, value: float, to_unit: Unit) -> float:
        """Convertit une valeur d'une unité vers une autre (si compatible).

        Args:
            value: Valeur numérique dans l'unité courante.
            to_unit: Unité cible.

        Returns:
            float: Valeur convertie.

        Raises:
            ValueError: Si les unités ne sont pas compatibles.
        """
        if not isinstance(to_unit, Unit):
            to_unit = Unit.from_any(to_unit)

        if self.category != to_unit.category:
            raise ValueError(
                f"Conversion impossible: {self.value} ({self.category}) -> "
                f"{to_unit.value} ({to_unit.category})"
            )

        if self.category == "count":
            # pas de conversion (1 pcs = 1 pcs)
            return float(value)

        # Tables de conversion vers une base interne
        if self.category == "mass":
            # base: gram
            to_gram = {
                Unit.MILLIGRAM: 0.001,
                Unit.GRAM: 1.0,
                Unit.KILOGRAM: 1000.0,
                Unit.OUNCE: 28.349523125,
                Unit.POUND: 453.59237,
            }
            grams = float(value) * to_gram[self]
            return grams / to_gram[to_unit]

        if self.category == "volume":
            # base: milliliter
            to_ml = {
                Unit.MILLILITER: 1.0,
                Unit.LITER: 1000.0,
                Unit.FLUID_OUNCE: 29.5735295625,  # US fl oz
            }
            ml = float(value) * to_ml[self]
            return ml / to_ml[to_unit]

        if self.category == "length":
            # base: centimeter
            to_cm = {
                Unit.CENTIMETER: 1.0,
                Unit.METER: 100.0,
            }
            cm = float(value) * to_cm[self]
            return cm / to_cm[to_unit]

        # devrait être unreachable
        return float(value)
