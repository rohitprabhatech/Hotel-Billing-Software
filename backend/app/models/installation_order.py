"""Installation jobs for electronics serial sales (BIZ-33)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_SCHEDULED = "SCHEDULED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_INSTALLATION_STATUSES = frozenset(
    {
        STATUS_SCHEDULED,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_SCHEDULED: {STATUS_IN_PROGRESS, STATUS_CANCELLED},
    STATUS_IN_PROGRESS: {STATUS_COMPLETED, STATUS_CANCELLED},
    STATUS_COMPLETED: set(),
    STATUS_CANCELLED: set(),
}


class InstallationNumberCounter(db.Model):
    __tablename__ = "installation_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class InstallationOrder(db.Model, TimestampMixin):
    __tablename__ = "installation_orders"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "installation_number", name="uq_installation_orders_tenant_number"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    installation_number: Mapped[str] = mapped_column(String(50), nullable=False)
    installation_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    serial_unit_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("serial_units.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=True, index=True
    )
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
    install_address: Mapped[str | None] = mapped_column(Text)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_SCHEDULED)
    notes: Mapped[str | None] = mapped_column(Text)
    technician_name: Mapped[str | None] = mapped_column(String(120))
    estimated_charge: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    serial_unit = relationship("SerialUnit", foreign_keys=[serial_unit_id])
    item = relationship("Item", foreign_keys=[item_id])
    custom_order = relationship("CustomProductOrder", foreign_keys=[custom_order_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    creator = relationship("User", foreign_keys=[created_by])
