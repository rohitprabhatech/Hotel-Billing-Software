"""Shared custom product orders — bakery cakes now; furniture later (BIZ-42)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

ORDER_TYPE_BAKERY = "bakery"
ORDER_TYPE_FURNITURE = "furniture"
ALLOWED_ORDER_TYPES = frozenset({ORDER_TYPE_BAKERY, ORDER_TYPE_FURNITURE})

STATUS_BOOKED = "BOOKED"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_IN_PRODUCTION = "IN_PRODUCTION"
STATUS_READY = "READY"
STATUS_DELIVERED = "DELIVERED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_CUSTOM_ORDER_STATUSES = frozenset(
    {
        STATUS_BOOKED,
        STATUS_CONFIRMED,
        STATUS_IN_PRODUCTION,
        STATUS_READY,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_BOOKED: {STATUS_CONFIRMED, STATUS_CANCELLED},
    STATUS_CONFIRMED: {STATUS_IN_PRODUCTION, STATUS_CANCELLED},
    STATUS_IN_PRODUCTION: {STATUS_READY, STATUS_CANCELLED},
    STATUS_READY: {STATUS_DELIVERED, STATUS_CANCELLED},
    STATUS_DELIVERED: set(),
    STATUS_CANCELLED: set(),
}


class CustomOrderNumberCounter(db.Model):
    __tablename__ = "custom_order_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class CustomProductOrder(db.Model, TimestampMixin):
    __tablename__ = "custom_product_orders"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "order_number", name="uq_custom_product_orders_tenant_number"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(30), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False, default=ORDER_TYPE_BAKERY)
    customer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    size: Mapped[str | None] = mapped_column(String(80))
    flavor: Mapped[str | None] = mapped_column(String(120))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("1"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    advance_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_BOOKED)
    notes: Mapped[str | None] = mapped_column(Text)
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    customer = relationship("Customer", foreign_keys=[customer_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])
    payments = relationship(
        "CustomOrderPayment",
        back_populates="custom_order",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="CustomOrderPayment.created_at",
    )


class CustomOrderPayment(db.Model):
    __tablename__ = "custom_order_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    custom_order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("custom_product_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False, default="cash")
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    custom_order = relationship("CustomProductOrder", back_populates="payments")
    creator = relationship("User", foreign_keys=[created_by])
