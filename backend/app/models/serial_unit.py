"""Serialized inventory units (IMEI / serial) — BIZ-29."""

from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_IN_STOCK = "IN_STOCK"
STATUS_SOLD = "SOLD"
STATUS_QUARANTINE = "QUARANTINE"
ALLOWED_SERIAL_STATUSES = frozenset({STATUS_IN_STOCK, STATUS_SOLD, STATUS_QUARANTINE})


class SerialUnit(db.Model, TimestampMixin):
    __tablename__ = "serial_units"
    __table_args__ = (
        UniqueConstraint("tenant_id", "serial", name="uq_serial_units_tenant_serial"),
        Index(
            "ix_serial_units_tenant_status_received",
            "tenant_id",
            "status",
            "received_at",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    serial: Mapped[str] = mapped_column(String(64), nullable=False)
    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=STATUS_IN_STOCK)
    sold_bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sold_bill_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bill_items.id", ondelete="SET NULL"), nullable=True
    )
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    item = relationship("Item", back_populates="serial_units")
