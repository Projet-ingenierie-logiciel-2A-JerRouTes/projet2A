from __future__ import annotations

from pydantic import BaseModel, Field


class RecipeIngredientOut(BaseModel):
    ingredient_id: int
    quantity: float


class RecipeTagOut(BaseModel):
    tag_id: int
    name: str


class RecipeOut(BaseModel):
    recipe_id: int
    creator_id: int
    status: str
    prep_time: int
    portions: int

    name: str = ""
    description: str = ""

    ingredients: list[RecipeIngredientOut] = Field(default_factory=list)
    tags: list[RecipeTagOut] = Field(default_factory=list)


class RecipeSearchIn(BaseModel):
    """Payload de recherche de recettes."""

    ingredients: list[str]
    limit: int = 10
    max_missing: int = 0
    strict_only: bool = False
    dish_type: str | None = None
    ignore_pantry: bool = True
