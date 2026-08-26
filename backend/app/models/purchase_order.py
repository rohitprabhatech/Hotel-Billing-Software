"""Purchase orders convertible to purchases (BIZ-52)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_DRAFT = "DRAFT"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_CONVERTED = "CONVERTED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_PURCHASE_ORDER_STATUSES = frozenset(
    {STATUS_DRAFT, STATUS_CONFIRMED, STATUS_CONVERTED, STATUS_CANCELLED}
)

STATUS_TRANSITIONS = {
    STATUS_DRAFT: {STATUS_CONFIRMED, STATUS_CANCELLED, STATUS_CONVERTED},
    STATUS_CONFIRMED: {STATUS_CANCELLED, STATUS_CONVERTED},
    STATUS_CONVERTED: set(),
    STATUS_CANCELLED: set(),
}


class PurchaseOrderNumberCounter(db.Model):
    __tablename__ = "purchase_order_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class PurchaseOrder(db.Model, TimestampMixin):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "order_number", name="uq_purchase_orders_tenant_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    order_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    supplier_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    supplier_name: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    expected_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_DRAFT)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    purchase_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    items = relationship("PurchaseOrderItem", back_populates="purchase_order", lazy="selectin")
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    purchase = relationship("Purchase", foreign_keys=[purchase_id])
    creator = relationship("User", foreign_keys=[created_by])


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    purchase_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    uom: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("Item", foreign_keys=[item_id])
