"""Delivery challans (BIZ-36)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_DRAFT = "DRAFT"
STATUS_DISPATCHED = "DISPATCHED"
STATUS_DELIVERED = "DELIVERED"
STATUS_CONVERTED = "CONVERTED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_CHALLAN_STATUSES = frozenset(
    {
        STATUS_DRAFT,
        STATUS_DISPATCHED,
        STATUS_DELIVERED,
        STATUS_CONVERTED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_DRAFT: {STATUS_DISPATCHED, STATUS_CANCELLED, STATUS_CONVERTED},
    STATUS_DISPATCHED: {STATUS_DELIVERED, STATUS_CANCELLED, STATUS_CONVERTED},
    STATUS_DELIVERED: {STATUS_CONVERTED},
    STATUS_CONVERTED: set(),
    STATUS_CANCELLED: set(),
}


class DeliveryChallanNumberCounter(db.Model):
    __tablename__ = "delivery_challan_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class DeliveryChallan(db.Model, TimestampMixin):
    __tablename__ = "delivery_challans"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "challan_number", name="uq_delivery_challans_tenant_number"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    challan_number: Mapped[str] = mapped_column(String(50), nullable=False)
    challan_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(30))
    delivery_address: Mapped[str | None] = mapped_column(Text)
    vehicle_number: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_DRAFT)
    quotation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    transport_charge: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    printed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    items = relationship("DeliveryChallanItem", back_populates="challan", lazy="selectin")
    customer = relationship("Customer", foreign_keys=[customer_id])
    quotation = relationship("Quotation", foreign_keys=[quotation_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])


class DeliveryChallanItem(db.Model):
    __tablename__ = "delivery_challan_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    challan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("delivery_challans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    uom: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    challan = relationship("DeliveryChallan", back_populates="items")
    item = relationship("Item", foreign_keys=[item_id])
