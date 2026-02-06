# src/services/find_recipe.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.backend.business_objects.recipe import Recipe


@dataclass(frozen=True)
class IngredientSearchQuery:
    ingredients: list[str]
    limit: int = 10
    max_missing: int = 0
    strict_only: bool = False  # si True -> mode findByIngredients (frigo strict)
    dish_type: str | None = None  # ex: "dessert"
    ignore_pantry: bool = True


class FindRecipe(ABC):
    @abstractmethod
    def get_by_id(self, recipe_id: int) -> Recipe | None:
        raise NotImplementedError

    @abstractmethod
    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        raise NotImplementedError
