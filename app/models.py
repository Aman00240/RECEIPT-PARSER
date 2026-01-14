from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, DateTime, ForeignKey
from datetime import datetime
from decimal import Decimal
from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_name: Mapped[str | None] = mapped_column()
    purchase_date: Mapped[datetime | None] = mapped_column(DateTime)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tax_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    scan_confidence: Mapped[float | None] = mapped_column()

    items: Mapped[list["Item"]] = relationship(
        "Item", back_populates="receipt", cascade="all, delete-orphan"
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE")
    )
    item_name: Mapped[str | None] = mapped_column()
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    category: Mapped[str | None] = mapped_column()

    receipt: Mapped["Receipt"] = relationship(back_populates="items")
