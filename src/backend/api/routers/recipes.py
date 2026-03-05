from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import CurrentUser, get_current_user_checked_exists, get_recipe_finder
from api.schemas.recipes import RecipeOut, RecipeSearchIn, RecipeUpdateIn
from business_objects.recipe import Recipe
from services.find_recipe import FindRecipe, IngredientSearchQuery


router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _extract_steps(r: Recipe) -> list[str]:
    # 1) Attribut direct (cas API externe)
    steps = list(getattr(r, "steps", []) or [])
    if steps:
        return [str(s).strip() for s in steps if str(s).strip()]

    # 2) Translations dédiées aux étapes (ex: "fr_steps", "en_steps", ...)
    if getattr(r, "translations", None):
        for k in ("fr_steps", "en_steps", "steps", "en_steps"):
            if k in r.translations:
                raw = str((r.translations.get(k) or {}).get("description") or "")
                if raw.strip():
                    return _split_steps_text(raw)

    # 3) Fallback: extraction depuis la description (si on a injecté "Préparation:")
    desc = ""
    if getattr(r, "translations", None):
        trans = r.translations.get("fr") or r.translations.get("en") or {}
        desc = str(trans.get("description") or "")

    if "Préparation:" in desc:
        after = desc.split("Préparation:", 1)[1]
        return _split_steps_text(after)

    return []


def _split_steps_text(raw: str) -> list[str]:
    lines = [ln.strip() for ln in str(raw).splitlines() if ln.strip()]
    out: list[str] = []
    for ln in lines:
        # Retire "1. ..." / "1) ..." / "- ..."
        ln = re.sub(r"^\s*(?:\d+\s*[\.|\)]\s*|[-•]\s*)", "", ln).strip()
        if ln:
            out.append(ln)
    return out


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
        steps=_extract_steps(r),
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
    #_cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
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
    #_cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
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


@router.get("", response_model=list[RecipeOut])
def list_recipes(
    limit: int = 50,
    offset: int = 0,
    name: str | None = None,
    include_relations: bool = False,
    #_cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """Liste toutes les recettes (BDD).

    - name : filtre sur le champ recipe.name (ILIKE)
    - include_relations : si True, recharge ingrédients + tags
    """
    from dao.recipe_dao import RecipeDAO

    dao = RecipeDAO()
    recipes = dao.list_recipes(name_ilike=name, limit=limit, offset=offset)

    if include_relations:
        full = []
        for r in recipes:
            rr = dao.get_recipe_by_id(int(r.recipe_id), with_relations=True)
            if rr is not None:
                full.append(rr)
        recipes = full

    return [_bo_to_out(r) for r in recipes]


@router.patch("/{recipe_id}", response_model=RecipeOut)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """Modification recette (admin uniquement)."""

    if cu.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )

    from dao.recipe_dao import RecipeDAO

    dao = RecipeDAO()
    updated = dao.update_recipe(
        int(recipe_id),
        name=payload.name,
        description=payload.description,
        prep_time=payload.prep_time,
        portion=payload.portions,
        status=payload.status,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recette introuvable.",
        )

    return _bo_to_out(updated)
