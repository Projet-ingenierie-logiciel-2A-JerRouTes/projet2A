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


router = APIRouter(prefix="/stocks", tags=["stocks"])


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
    cu: CurrentUser = Depends(get_current_user_checked_exists),  # noqa: B008
):
    # Ici on utilise StockDAO directement (simple)
    from src.backend.dao.stock_dao import StockDAO

    dao = StockDAO()
    stocks = dao.list_user_stocks(
        user_id=cu.user_id, name_ilike=None, limit=200, offset=0
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
