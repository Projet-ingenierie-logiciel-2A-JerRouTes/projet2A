from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.api.deps import (
    CurrentUser,
    get_current_user_checked_exists,
    get_stock_service,
)
from src.backend.api.schemas.stocks import (
    ConsumeIn,
    StockCreateIn,
    StockItemCreateIn,
    StockItemOut,
    StockOut,
)
from src.backend.services.stock_service import (
    ForbiddenError,
    NotFoundError,
    StockService,
    ValidationError,
)


router = APIRouter(prefix="/stocks", tags=["Stocks"])


def _map_service_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, ForbiddenError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
    )


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel inventaire (stock)",
    response_description="L'identifiant du stock nouvellement créé",
    responses={
        401: {"description": "Utilisateur non authentifié"},
        500: {"description": "Erreur interne lors de la création du stock"},
    },
)
def create_stock(
    payload: StockCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """
    Initialise un nouveau stock (frigo/cellier) pour l'utilisateur connecté.

    - **name**: Le nom personnalisé du stock (ex: 'Frigo Cuisine', 'Cellier')

    Cette route :
    1. Vérifie l'existence de l'utilisateur via le token.
    2. Appelle le service métier pour créer l'entrée en base de données.
    3. Lie automatiquement le nouveau stock à l'utilisateur `cu`.
    """
    try:
        stock_id = service.create_stock_for_user(user_id=cu.user_id, name=payload.name)
        return {"stock_id": stock_id}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.get(
    "",
    # Le type list[StockOut] assure que le frontend reçoit un tableau d'objets bien
    # structurés
    response_model=list[StockOut],
    summary="Lister mes inventaires",
    response_description="La liste des stocks (frigos, celliers) appartenant à "
    "l'utilisateur",
)
def list_my_stocks(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """
    Récupère tous les stocks associés au compte de l'utilisateur connecté.

    - **Pagination**: Par défaut limitée aux 200 premiers résultats.
    - **Filtrage**: Retourne tous les stocks sans filtre de nom par défaut.

    Cette route interroge directement la couche DAO pour une récupération rapide des
    données
    de propriété (ID et Nom du stock).
    """
    # Ici on utilise StockDAO directement (simple)
    from src.backend.dao.stock_dao import StockDAO

    dao = StockDAO()
    stocks = dao.list_user_stocks(
        user_id=cu.user_id, name_ilike=None, limit=200, offset=0
    )
    return [StockOut(stock_id=s.id_stock, name=s.nom) for s in stocks]


@router.get(
    "/by-name/{name}",
    response_model=StockOut | None,
    summary="Chercher un stock par son nom",
    description="Recherche un inventaire spécifique appartenant à l'utilisateur via "
    "son nom exact.",
    response_description="L'objet Stock correspondant ou null si aucun résultat n'est"
    " trouvé",
)
def get_my_stock_by_name(
    name: str,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """
    Recherche un stock parmi ceux appartenant à l'utilisateur connecté.

    - **name**: Le nom exact du stock recherché (ex: 'Frigo').
    - **with_items**: Par défaut à False, cette route ne récupère pas le détail du
    contenu pour optimiser la performance.

    Cette route est utile pour vérifier l'existence d'un stock avant une création ou
    pour récupérer un ID à partir d'un nom connu.
    """
    stock = service.get_user_stock_by_name(
        user_id=cu.user_id, name=name, with_items=False
    )
    if stock is None:
        return None
    return StockOut(stock_id=stock.id_stock, name=stock.nom)


@router.get("/{stock_id}/lots", response_model=list[StockItemOut])
def list_lots(
    stock_id: int,
    ingredient_id: int | None = None,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    try:
        lots = service.list_lots(
            user_id=cu.user_id, stock_id=stock_id, ingredient_id=ingredient_id
        )
        return [
            StockItemOut(
                stock_item_id=lot.stock_item_id,
                stock_id=lot.fk_stock_id,
                ingredient_id=lot.fk_ingredient_id,
                quantity=float(lot.quantity),
                expiration_date=lot.expiration_date,
            )
            for lot in lots
        ]
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


# @router.post("/{stock_id}/lots", response_model=dict)
@router.get(
    "/{stock_id}/lots",
    # response_model=list[StockItemOut],
    response_model=dict,
    summary="Lister les lots d'un stock",
    description="Récupère tous les articles (lots) présents dans un stock spécifique, "
    "avec un filtrage optionnel par ingrédient.",
    response_description="La liste des lots correspondant aux critères",
)
def add_lot(
    stock_id: int,
    payload: StockItemCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """
    Consulte le contenu d'un frigo ou d'un cellier.

    - **stock_id**: L'identifiant unique du stock à consulter.
    - **ingredient_id**: (Optionnel) Permet de ne lister que les lots d'un ingrédient
    précis (ex: voir toutes les briques de lait).

    **Sécurité :**
    Le service vérifie automatiquement que le `stock_id` appartient bien à l'utilisateur
     `cu`.
    """
    try:
        lot_id = service.add_lot(
            user_id=cu.user_id,
            stock_id=stock_id,
            ingredient_id=payload.ingredient_id,
            quantity=payload.quantity,
            expiration_date=payload.expiration_date,
        )
        return {"stock_item_id": lot_id}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.delete(
    "/lots/{stock_item_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Supprimer un lot du stock",
    description="Supprime définitivement un article (lot) spécifique d'un inventaire.",
    response_description="Confirmation de la suppression",
    responses={
        403: {"description": "Interdit - Ce lot n'appartient pas à l'utilisateur"},
        404: {"description": "Lot non trouvé"},
    },
)
def delete_lot(
    stock_item_id: int,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """
    Retire un lot de votre frigo ou cellier.

    - **stock_item_id**: L'identifiant unique du lot à supprimer.

    **Sécurité :**
    Le `StockService` vérifie que le lot appartient bien à un stock détenu par
    l'utilisateur `cu` avant de procéder à la suppression.
    """
    try:
        deleted = service.delete_lot(user_id=cu.user_id, stock_item_id=stock_item_id)
        return {"deleted": deleted}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.post(
    "/{stock_id}/consume",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Consommer un ingrédient (Logique FEFO)",
    description="Consomme une quantité donnée d'un ingrédient en utilisant prioritairement les lots dont la date d'expiration est la plus proche.",
    response_description="Détail de la consommation effectuée",
    responses={
        400: {"description": "Quantité insuffisante en stock"},
        404: {"description": "Stock ou ingrédient non trouvé"},
        403: {"description": "Accès refusé à ce stock"},
    },
)
def consume_fefo(
    stock_id: int,
    payload: ConsumeIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """
    Déduit une quantité d'un ingrédient du stock de l'utilisateur.

    - **stock_id**: L'inventaire concerné.
    - **ingredient_id**: L'ingrédient à consommer.
    - **quantity**: La quantité totale à retirer.

    L'algorithme **FEFO** (First Expired, First Out) garantit que les produits périssables sont utilisés dans le bon ordre.
    """
    try:
        res = service.consume_fefo(
            user_id=cu.user_id,
            stock_id=stock_id,
            ingredient_id=payload.ingredient_id,
            quantity=payload.quantity,
        )
        return {
            "stock_id": res.stock_id,
            "ingredient_id": res.ingredient_id,
            "consumed_quantity": res.consumed_quantity,
        }
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc
