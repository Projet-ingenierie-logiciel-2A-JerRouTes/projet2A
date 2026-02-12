from __future__ import annotations

from pydantic import BaseModel, Field


class IngredientOut(BaseModel):
    """
    Structure d'un ingrédient telle qu'elle apparaît dans le catalogue.
    """

    ingredient_id: int = Field(
        title="ID Ingrédient",
        description="Identifiant unique en base de données",
        example=42,
    )
    name: str = Field(
        title="Nom de l'ingrédient",
        description="Nom complet (ex: Farine de blé, Lait demi-écrémé)",
        example="Farine de blé",
    )
    unit: str | None = Field(
        default=None,
        title="Unité de mesure",
        description="Unité par défaut (g, ml, unité)",
        example="g",
    )
    tag_ids: list[int] = Field(
        default_factory=list,
        title="Tags associés",
        description="Liste des IDs de catégories (Légumes, Frais, etc.)",
        example=[1, 5],
    )


class IngredientCreateIn(BaseModel):
    """
    Données nécessaires pour ajouter un nouvel ingrédient au référentiel.
    """

    name: str = Field(
        min_length=1,
        title="Nom de l'ingrédient",
        description="Le nom doit être unique dans le catalogue",
        example="Poivre noir",
    )
    unit: str | None = Field(
        default=None,
        title="Unité",
        description="Unité de mesure de référence",
        example="g",
    )
    tag_ids: list[int] = Field(
        default_factory=list,
        title="IDs des Tags",
        description="Liste des identifiants de tags à lier à la création",
        example=[],
    )
