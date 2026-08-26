"""Repair / service tickets for serialized goods (BIZ-31)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_RECEIVED = "RECEIVED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_READY = "READY"
STATUS_DELIVERED = "DELIVERED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_REPAIR_STATUSES = frozenset(
    {
        STATUS_RECEIVED,
        STATUS_IN_PROGRESS,
        STATUS_READY,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_RECEIVED: {STATUS_IN_PROGRESS, STATUS_CANCELLED},
    STATUS_IN_PROGRESS: {STATUS_READY, STATUS_CANCELLED},
    STATUS_READY: {STATUS_DELIVERED, STATUS_CANCELLED},
    STATUS_DELIVERED: set(),
    STATUS_CANCELLED: set(),
}


class RepairNumberCounter(db.Model):
    __tablename__ = "repair_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class RepairOrder(db.Model, TimestampMixin):
    __tablename__ = "repair_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "repair_number", name="uq_repair_orders_tenant_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    repair_number: Mapped[str] = mapped_column(String(50), nullable=False)
    repair_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    serial_unit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("serial_units.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(30))
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_RECEIVED)
    notes: Mapped[str | None] = mapped_column(Text)
    estimated_charge: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    serial_unit = relationship("SerialUnit", foreign_keys=[serial_unit_id])
    item = relationship("Item", foreign_keys=[item_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])
