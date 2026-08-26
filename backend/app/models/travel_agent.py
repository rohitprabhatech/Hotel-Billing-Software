"""Travel agents and commission entries (BIZ-59)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

COMMISSION_PENDING = "PENDING"
COMMISSION_PAID = "PAID"
COMMISSION_CANCELLED = "CANCELLED"

ALLOWED_COMMISSION_STATUSES = frozenset(
    {COMMISSION_PENDING, COMMISSION_PAID, COMMISSION_CANCELLED}
)


class TravelAgent(db.Model, TimestampMixin):
    __tablename__ = "travel_agents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_travel_agents_tenant_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(160))
    commission_percent: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=Decimal("0.00")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    commission_entries = relationship(
        "TravelCommissionEntry",
        back_populates="agent",
        lazy="dynamic",
    )


class TravelCommissionEntry(db.Model):
    """Commission accrued against a booking for an agent."""

    __tablename__ = "travel_commission_entries"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "booking_id",
            name="uq_travel_commission_entries_tenant_booking",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("travel_agents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    booking_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("travel_bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    booking_number: Mapped[str] = mapped_column(String(30), nullable=False)
    booking_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=COMMISSION_PENDING
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    agent = relationship("TravelAgent", back_populates="commission_entries")
    booking = relationship("TravelBooking", back_populates="commission_entry")
    creator = relationship("User", foreign_keys=[created_by])
