"""Sales returns and exchanges (BIZ-27)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

KIND_RETURN = "RETURN"
KIND_EXCHANGE = "EXCHANGE"
ALLOWED_RETURN_KINDS = frozenset({KIND_RETURN, KIND_EXCHANGE})


class SalesReturnCounter(db.Model):
    __tablename__ = "sales_return_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class SalesReturn(db.Model, TimestampMixin):
    __tablename__ = "sales_returns"
    __table_args__ = (
        UniqueConstraint("tenant_id", "return_number", name="uq_sales_returns_tenant_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    return_number: Mapped[str] = mapped_column(String(50), nullable=False)
    return_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default=KIND_RETURN)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    extra_payable: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="FINALIZED")
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    items = relationship("SalesReturnItem", back_populates="sales_return", lazy="selectin")
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])


class SalesReturnItem(db.Model):
    __tablename__ = "sales_return_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    return_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sales_returns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bill_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bill_items.id", ondelete="RESTRICT"), nullable=False
    )
    item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("items.id", ondelete="SET NULL"))
    variant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("item_variants.id", ondelete="SET NULL")
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    line_refund: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    exchange_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="SET NULL")
    )
    exchange_variant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("item_variants.id", ondelete="SET NULL")
    )
    exchange_item_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    sales_return = relationship("SalesReturn", back_populates="items")
