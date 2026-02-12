from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.api.deps import CurrentUser, get_current_user_checked_exists
from src.backend.api.schemas.ingredients import IngredientCreateIn, IngredientOut
from src.backend.dao.ingredient_dao import IngredientDAO


router = APIRouter(prefix="/ingredients")


@router.get(
    "",
    response_model=list[IngredientOut],
    summary="Lister le référentiel des ingrédients",
    response_description="La liste complète des ingrédients disponibles dans le catalogue global",
    tags=["Ingredient"],
)
def list_ingredients(
    _cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """
    Récupère l'intégralité des ingrédients enregistrés dans le système.

    - **Accès**: Nécessite d'être authentifié.
    - **Usage**: Utile pour remplir les listes déroulantes ou l'autocomplétion dans le frontend.

    *Note: Actuellement en cours de développement.*
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Route non implémentée: ajouter IngredientDAO.list_ingredients().",
    )


@router.post(
    "",
    response_model=IngredientOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel ingrédient",
    response_description="L'ingrédient créé avec son ID unique",
    responses={
        403: {"description": "Accès refusé - Droits administrateur requis"},
        400: {"description": "Données invalides (ex: nom déjà utilisé)"},
    },
    tags=["Ingredient"],
)
def create_ingredient(
    payload: IngredientCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """
    Ajoute un nouvel ingrédient au référentiel global.

    - **name**: Nom unique de l'ingrédient (ex: 'Farine de blé')
    - **unit**: Unité de mesure par défaut (g, ml, unité...)
    - **tag_ids**: Liste d'identifiants de catégories (ex: [1, 5] pour 'Frais' et 'Légumes')

    **Sécurité :**
    Cette route est strictement réservée aux utilisateurs ayant le statut **admin**.
    """
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
