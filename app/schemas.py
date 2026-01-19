from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class ItemBase(BaseModel):
    item_name: str | None = None
    price: Decimal | None = None
    category: str | None = None


class ReceiptCreate(BaseModel):
    store_name: str | None = None
    currency_symbol: str | None = "$"
    purchase_date: datetime | None = None
    total_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    scan_confidence: float | None = None

    items: list[ItemBase] = []
