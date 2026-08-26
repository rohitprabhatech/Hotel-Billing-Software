"""Furniture delivery jobs linked to custom orders (BIZ-49)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_SCHEDULED = "SCHEDULED"
STATUS_OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
STATUS_DELIVERED = "DELIVERED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_DELIVERY_STATUSES = frozenset(
    {
        STATUS_SCHEDULED,
        STATUS_OUT_FOR_DELIVERY,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_SCHEDULED: {STATUS_OUT_FOR_DELIVERY, STATUS_CANCELLED},
    STATUS_OUT_FOR_DELIVERY: {STATUS_DELIVERED, STATUS_CANCELLED},
    STATUS_DELIVERED: set(),
    STATUS_CANCELLED: set(),
}

ACTIVE_DELIVERY_STATUSES = frozenset({STATUS_SCHEDULED, STATUS_OUT_FOR_DELIVERY})


class DeliveryNumberCounter(db.Model):
    __tablename__ = "delivery_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class DeliveryJob(db.Model, TimestampMixin):
    __tablename__ = "delivery_jobs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "delivery_number", name="uq_delivery_jobs_tenant_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    delivery_number: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    custom_order_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("custom_product_orders.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(30))
    delivery_address: Mapped[str | None] = mapped_column(Text)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_SCHEDULED)
    driver_name: Mapped[str | None] = mapped_column(String(120))
    vehicle_number: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    out_for_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    custom_order = relationship("CustomProductOrder", foreign_keys=[custom_order_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])
