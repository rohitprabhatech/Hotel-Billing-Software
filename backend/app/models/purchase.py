"""Purchase header and line models + per-tenant purchase number counter."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

PURCHASE_FINALIZED = "FINALIZED"
PURCHASE_CANCELLED = "CANCELLED"


class PurchaseNumberCounter(db.Model):
    __tablename__ = "purchase_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class Purchase(db.Model, TimestampMixin):
    __tablename__ = "purchases"
    __table_args__ = (
        UniqueConstraint("tenant_id", "purchase_number", name="uq_purchases_tenant_number"),
        UniqueConstraint("tenant_id", "purchase_sequence", name="uq_purchases_tenant_sequence"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    purchase_number: Mapped[str] = mapped_column(String(50), nullable=False)
    purchase_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("suppliers.id", ondelete="SET NULL"), index=True
    )
    supplier_name: Mapped[str | None] = mapped_column(String(120))
    invoice_number: Mapped[str | None] = mapped_column(String(60))
    notes: Mapped[str | None] = mapped_column(Text)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=PURCHASE_FINALIZED)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    cancelled_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT")
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)

    items = relationship("PurchaseItem", back_populates="purchase", lazy="selectin")
    supplier = relationship("Supplier")
    creator = relationship("User", foreign_keys=[created_by])


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    purchase_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("purchases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    purchase = relationship("Purchase", back_populates="items")
    item = relationship("Item")
