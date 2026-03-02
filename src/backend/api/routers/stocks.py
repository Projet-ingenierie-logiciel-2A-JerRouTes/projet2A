from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import (
    CurrentUser,
    get_current_user_checked_exists,
    get_stock_service,
)
from api.schemas.ingredients import IngredientOwnedOut
from api.schemas.stocks import (
    ConsumeIn,
    StockCreateIn,
    StockItemCreateIn,
    StockItemOut,
    StockOut,
    StockUpdateIn,
)
from services.stock_service import (
    ForbiddenError,
    NotFoundError,
    StockService,
    ValidationError,
)


router = APIRouter(prefix="/api/stocks", tags=["stocks"])


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


@router.post("", response_model=dict)
def create_stock(
    payload: StockCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    try:
        stock_id = service.create_stock_for_user(user_id=cu.user_id, name=payload.name)
        return {"stock_id": stock_id}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.get("", response_model=list[StockOut])
def list_my_stocks(
    user_id: int | None = None,
    limit: int = 200,
    offset: int = 0,
    name: str | None = None,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """
    - Sans user_id : retourne les stocks de l'utilisateur connecté (comme avant)
    - Avec user_id : admin uniquement (si user_id != cu.user_id)
    """
    from dao.stock_dao import StockDAO

    target_user_id = cu.user_id if user_id is None else int(user_id)

    # Si on demande les stocks d'un autre user => admin only
    if target_user_id != cu.user_id and cu.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )

    dao = StockDAO()
    stocks = dao.list_user_stocks(
        user_id=target_user_id,
        name_ilike=name,
        limit=limit,
        offset=offset,
    )
    return [StockOut(stock_id=s.id_stock, name=s.nom) for s in stocks]


@router.get("/by-name/{name}", response_model=StockOut | None)
def get_my_stock_by_name(
    name: str,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
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


@router.post("/{stock_id}/lots", response_model=dict)
def add_lot(
    stock_id: int,
    payload: StockItemCreateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
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


@router.delete("/lots/{stock_item_id}", response_model=dict)
def delete_lot(
    stock_item_id: int,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    try:
        deleted = service.delete_lot(user_id=cu.user_id, stock_item_id=stock_item_id)
        return {"deleted": deleted}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.post("/{stock_id}/consume", response_model=dict)
def consume_fefo(
    stock_id: int,
    payload: ConsumeIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
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


@router.delete("/{stock_id}", response_model=dict)
def delete_stock(
    stock_id: int,
    cu: CurrentUser = Depends(get_current_user_checked_exists),
    service: StockService = Depends(get_stock_service),
):
    try:
        deleted = service.delete_stock(user_id=cu.user_id, stock_id=stock_id)
        return {"deleted": deleted}
    except Exception as exc:
        raise _map_service_errors(exc) from exc


@router.delete("/{stock_id}/lots", response_model=dict)
def empty_stock(
    stock_id: int,
    cu: CurrentUser = Depends(get_current_user_checked_exists),
    service: StockService = Depends(get_stock_service),
):
    try:
        deleted_count = service.empty_stock(user_id=cu.user_id, stock_id=stock_id)
        return {"deleted_lots": deleted_count}
    except Exception as exc:
        raise _map_service_errors(exc) from exc


@router.get("/all", response_model=list[StockOut])
def list_all_stocks(
    limit: int = 50,
    offset: int = 0,
    name: str | None = None,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    """Liste tous les stocks (admin uniquement)."""

    if cu.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )

    from dao.stock_dao import StockDAO

    dao = StockDAO()
    stocks = dao.list_stocks(
        name_ilike=name,
        limit=limit,
        offset=offset,
    )

    return [
        StockOut(
            stock_id=s.id_stock,
            name=s.nom,
        )
        for s in stocks
    ]


@router.get("/ingredients", response_model=list[IngredientOwnedOut])
def list_my_ingredients(
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """Retourne tous les ingrédients présents dans les stocks de l'utilisateur."""
    try:
        rows = service.list_user_ingredients(user_id=cu.user_id)
        return [
            IngredientOwnedOut(
                ingredient_id=r.ingredient_id,
                name=r.name,
                unit=r.unit,
                tag_ids=r.tag_ids,
                total_quantity=float(r.total_quantity or 0.0),
            )
            for r in rows
        ]
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc


@router.get("/ingredients/names")
def list_my_ingredient_names(
    cu: CurrentUser = Depends(get_current_user_checked_exists),
    service: StockService = Depends(get_stock_service),
):
    rows = service.list_user_ingredient_names(user_id=cu.user_id)

    return [
        {
            "ingredient_id": r["ingredient_id"],
            "name": r["name"],
        }
        for r in rows
    ]


@router.patch("/{stock_id}", response_model=dict)
def update_stock_name(
    stock_id: int,
    payload: StockUpdateIn,
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
    service: StockService = Depends(get_stock_service),  # noqa: B008
):
    """Modifie le nom d'un stock (admin uniquement)."""

    if not cu.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )

    try:
        service.update_stock_name(stock_id=stock_id, name=payload.name)
        return {"updated": True}
    except Exception as exc:  # noqa: BLE001
        raise _map_service_errors(exc) from exc
