"""Kitchen Order Ticket models (BIZ-14)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.kots import KOT_STATUS_QUEUED
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class KotNumberCounter(db.Model):
    __tablename__ = "kot_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class Kot(db.Model, TimestampMixin):
    __tablename__ = "kots"
    __table_args__ = (
        UniqueConstraint("tenant_id", "kot_number", name="uq_kots_tenant_number"),
        UniqueConstraint("tenant_id", "kot_sequence", name="uq_kots_tenant_sequence"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    kot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    kot_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=KOT_STATUS_QUEUED)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    dining_table_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("dining_tables.id", ondelete="SET NULL"), index=True
    )
    dining_table_code: Mapped[str | None] = mapped_column(String(32))
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    print_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    printed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    items = relationship("KotItem", back_populates="kot", lazy="selectin", cascade="all, delete-orphan")
    order = relationship("Order")
    dining_table = relationship("DiningTable")
    creator = relationship("User", foreign_keys=[created_by])


class KotItem(db.Model):
    __tablename__ = "kot_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    kot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    kot = relationship("Kot", back_populates="items")
    order_item = relationship("OrderItem")
    item = relationship("Item")
