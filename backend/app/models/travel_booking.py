"""Travel bookings and payments (BIZ-57)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

STATUS_BOOKED = "BOOKED"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELLED = "CANCELLED"

ALLOWED_TRAVEL_BOOKING_STATUSES = frozenset(
    {
        STATUS_BOOKED,
        STATUS_CONFIRMED,
        STATUS_IN_PROGRESS,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
    }
)

STATUS_TRANSITIONS = {
    STATUS_BOOKED: {STATUS_CONFIRMED, STATUS_CANCELLED},
    STATUS_CONFIRMED: {STATUS_IN_PROGRESS, STATUS_CANCELLED},
    STATUS_IN_PROGRESS: {STATUS_COMPLETED, STATUS_CANCELLED},
    STATUS_COMPLETED: set(),
    STATUS_CANCELLED: set(),
}


class TravelBookingNumberCounter(db.Model):
    __tablename__ = "travel_booking_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TravelBooking(db.Model, TimestampMixin):
    __tablename__ = "travel_bookings"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "booking_number", name="uq_travel_bookings_tenant_number"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    booking_number: Mapped[str] = mapped_column(String(30), nullable=False)
    booking_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    package_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tour_packages.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    package_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(30))
    pax_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    travel_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), index=True)
    travel_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    advance_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_BOOKED)
    notes: Mapped[str | None] = mapped_column(Text)
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("travel_agents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    package = relationship("TourPackage", foreign_keys=[package_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    bill = relationship("Bill", foreign_keys=[bill_id])
    agent = relationship("TravelAgent", foreign_keys=[agent_id])
    creator = relationship("User", foreign_keys=[created_by])
    payments = relationship(
        "TravelBookingPayment",
        back_populates="booking",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="TravelBookingPayment.created_at",
    )
    itinerary_items = relationship(
        "TravelItineraryItem",
        back_populates="booking",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="TravelItineraryItem.sort_order, TravelItineraryItem.day_number",
    )
    documents = relationship(
        "TravelBookingDocument",
        back_populates="booking",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="TravelBookingDocument.created_at",
    )
    commission_entry = relationship(
        "TravelCommissionEntry",
        back_populates="booking",
        lazy="selectin",
        uselist=False,
        cascade="all, delete-orphan",
    )


class TravelBookingPayment(db.Model):
    __tablename__ = "travel_booking_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    booking_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("travel_bookings.id", ondelete="CASCADE"),
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

    booking = relationship("TravelBooking", back_populates="payments")
    creator = relationship("User", foreign_keys=[created_by])
