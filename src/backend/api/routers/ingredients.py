from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import CurrentUser, get_current_user_checked_exists
from api.schemas.ingredients import IngredientCreateIn, IngredientOut
from dao.ingredient_dao import IngredientDAO


router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

# ==========================================================
# LISTE DES INGRÉDIENTS
# ==========================================================


@router.get("", response_model=list[IngredientOut])
def list_ingredients(
    _cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """
    Retourne la liste complète des ingrédients disponibles.
    Accessible à tout utilisateur authentifié.
    """
    dao = IngredientDAO()
    ingredients = dao.list_ingredients(with_tags=True)

    return [
        IngredientOut(
            ingredient_id=ing.id_ingredient,
            name=ing.name,
            unit=ing.unit.value,  # Enum → string
            tag_ids=ing.id_tags,
        )
        for ing in ingredients
    ]


@router.post("", response_model=IngredientOut)
def create_ingredient(
    payload: IngredientCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    if cu.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un admin peut créer un ingrédient.",
        )

    dao = IngredientDAO()
    ing = dao.create_ingredient(
        name=payload.name,
        unit=payload.unit,
        tag_ids=payload.tag_ids,
    )

    return IngredientOut(
        ingredient_id=ing.id_ingredient,
        name=ing.name,
        unit=ing.unit.value,
        tag_ids=ing.id_tags,
    )
