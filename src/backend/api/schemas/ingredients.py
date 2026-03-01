from __future__ import annotations

from pydantic import BaseModel, Field


class IngredientOut(BaseModel):
    ingredient_id: int
    name: str
    unit: str | None = None
    tag_ids: list[int] = Field(default_factory=list)


class IngredientCreateIn(BaseModel):
    name: str
    unit: str | None = None
    tag_ids: list[int] = Field(default_factory=list)


class IngredientOwnedOut(IngredientOut):
    """Ingrédient présent dans les stocks de l'utilisateur, avec quantité totale."""

    total_quantity: float
