from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class StockCreateIn(BaseModel):
    name: str


class StockOut(BaseModel):
    stock_id: int
    name: str


class StockItemCreateIn(BaseModel):
    ingredient_id: int
    quantity: float
    expiration_date: date | None = None


class StockItemOut(BaseModel):
    stock_item_id: int
    stock_id: int
    ingredient_id: int
    quantity: float
    expiration_date: date | None = None


class ConsumeIn(BaseModel):
    ingredient_id: int
    quantity: float
