from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class StockCreateIn(BaseModel):
    """
    Données nécessaires pour initialiser un nouvel emplacement de stockage.
    """

    name: str = Field(
        ...,
        min_length=1,
        title="Nom du stock",
        description="Nom descriptif (ex: 'Frigo Cuisine', 'Réserve')",
        example="Frigo Principal",
    )


class StockOut(BaseModel):
    """
    Représentation simplifiée d'un stock pour les listes de sélection.
    """

    stock_id: int = Field(
        title="ID Stock", description="Identifiant unique de l'inventaire"
    )
    name: str = Field(title="Nom", description="Nom attribué au stock")


class StockItemCreateIn(BaseModel):
    """
    Données pour l'ajout d'un nouveau lot d'ingrédient dans un stock.
    """

    ingredient_id: int = Field(
        ...,
        title="ID Ingrédient",
        description="L'identifiant du produit provenant du référentiel",
        example=12,
    )
    quantity: float = Field(
        ...,
        gt=0,
        title="Quantité",
        description="Volume ou poids ajouté au stock",
        example=500.0,
    )
    expiration_date: date | None = Field(
        default=None,
        title="Date d'expiration",
        description="Date limite de consommation (format ISO: YYYY-MM-DD)",
        example="2026-06-30",
    )


class StockItemOut(BaseModel):
    """
    Détail complet d'un lot (item) présent en stock.
    """

    stock_item_id: int = Field(
        title="ID Lot", description="Identifiant unique du lot en stock"
    )
    stock_id: int = Field(
        title="ID Stock", description="Référence au stock contenant ce lot"
    )
    ingredient_id: int = Field(
        title="ID Ingrédient", description="Référence au type d'ingrédient"
    )
    quantity: float = Field(
        title="Quantité", description="Quantité restante dans ce lot spécifique"
    )
    expiration_date: date | None = Field(
        title="Péremption", description="Date limite de consommation du lot"
    )


class ConsumeIn(BaseModel):
    """
    Paramètres pour la consommation intelligente (FEFO) d'un ingrédient.
    """

    ingredient_id: int = Field(
        ...,
        title="ID Ingrédient",
        description="L'ingrédient que vous souhaitez utiliser",
        example=12,
    )
    quantity: float = Field(
        ...,
        gt=0,
        title="Quantité à consommer",
        description="Le système déduira cette quantité des lots les plus proches de la péremption",
        example=150.5,
    )
