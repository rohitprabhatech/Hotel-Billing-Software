"""Food wastage entries (BIZ-18)."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class WastageEntry(db.Model, TimestampMixin):
    __tablename__ = "wastage_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80))
    wastage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    stock_movement_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("stock_movements.id", ondelete="SET NULL"), index=True
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    item = relationship("Item", foreign_keys=[item_id])
    stock_movement = relationship("StockMovement", foreign_keys=[stock_movement_id])
    creator = relationship("User", foreign_keys=[created_by])
