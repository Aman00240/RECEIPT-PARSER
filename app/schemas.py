from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


class ItemBase(BaseModel):
    item_name: str | None = None
    price: Decimal | None = None
    category: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)


class ReceiptBase(BaseModel):
    store_name: str | None = None
    purchase_date: datetime | None = None
    total_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    scan_confidence: float | None = None


class ReceiptCreate(ReceiptBase):
    items: list[ItemCreate] = []


class ReceiptResponse(ReceiptBase):
    id: int
    items: list[ItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
