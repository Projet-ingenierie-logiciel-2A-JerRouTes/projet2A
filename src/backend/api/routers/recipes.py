from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import CurrentUser, get_current_user_checked_exists, get_recipe_finder
from api.schemas.recipes import RecipeOut, RecipeSearchIn
from business_objects.recipe import Recipe
from services.find_recipe import FindRecipe, IngredientSearchQuery


router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _bo_to_out(r: Recipe) -> RecipeOut:
    # Nom / description : on privilégie le FR, sinon EN, sinon vide
    name = ""
    description = ""
    if getattr(r, "translations", None):
        trans = r.translations.get("fr") or r.translations.get("en") or {}
        name = str(trans.get("name") or "")
        description = str(trans.get("description") or "")

    return RecipeOut(
        recipe_id=int(r.recipe_id),
        creator_id=int(r.creator_id),
        status=str(r.status),
        prep_time=int(r.prep_time),
        portions=int(r.portions),
        name=name,
        description=description,
        ingredients=[
            {"ingredient_id": int(iid), "quantity": float(qty)}
            for iid, qty in (getattr(r, "ingredients", []) or [])
        ],
        tags=[
            {"tag_id": int(tid), "name": str(tname)}
            for tid, tname in (getattr(r, "tags", []) or [])
        ],
    )


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(
    recipe_id: int,
    _cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    finder: FindRecipe = Depends(get_recipe_finder),  # noqa: B008
):
    r = finder.get_by_id(int(recipe_id))
    if r is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recette introuvable.",
        )
    return _bo_to_out(r)


@router.post("/search", response_model=list[RecipeOut])
def search_recipes(
    payload: RecipeSearchIn,
    _cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    finder: FindRecipe = Depends(get_recipe_finder),  # noqa: B008
):
    query = IngredientSearchQuery(
        ingredients=payload.ingredients,
        limit=payload.limit,
        max_missing=payload.max_missing,
        strict_only=payload.strict_only,
        dish_type=payload.dish_type,
        ignore_pantry=payload.ignore_pantry,
    )
    res = finder.search_by_ingredients(query)
    return [_bo_to_out(r) for r in res]
