"""Travel booking itinerary items and document metadata (BIZ-58)."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

ITINERARY_HOTEL = "HOTEL"
ITINERARY_VEHICLE = "VEHICLE"
ITINERARY_TICKET = "TICKET"
ITINERARY_ACTIVITY = "ACTIVITY"
ITINERARY_OTHER = "OTHER"

ALLOWED_ITINERARY_TYPES = frozenset(
    {
        ITINERARY_HOTEL,
        ITINERARY_VEHICLE,
        ITINERARY_TICKET,
        ITINERARY_ACTIVITY,
        ITINERARY_OTHER,
    }
)

DOC_PASSPORT = "PASSPORT"
DOC_VISA = "VISA"
DOC_ID = "ID"
DOC_TICKET_COPY = "TICKET_COPY"
DOC_OTHER = "OTHER"

ALLOWED_DOCUMENT_TYPES = frozenset(
    {
        DOC_PASSPORT,
        DOC_VISA,
        DOC_ID,
        DOC_TICKET_COPY,
        DOC_OTHER,
    }
)


class TravelItineraryItem(db.Model, TimestampMixin):
    __tablename__ = "travel_itinerary_items"

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
    item_type: Mapped[str] = mapped_column(String(20), nullable=False, default=ITINERARY_ACTIVITY)
    day_number: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(200))
    vendor_name: Mapped[str | None] = mapped_column(String(160))
    confirmation_ref: Mapped[str | None] = mapped_column(String(120))
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    booking = relationship("TravelBooking", back_populates="itinerary_items")


class TravelBookingDocument(db.Model):
    """Document metadata only — no binary storage (PII encrypt-at-rest later)."""

    __tablename__ = "travel_booking_documents"

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
    document_type: Mapped[str] = mapped_column(String(30), nullable=False, default=DOC_OTHER)
    holder_name: Mapped[str | None] = mapped_column(String(120))
    document_number: Mapped[str | None] = mapped_column(String(80))
    issued_country: Mapped[str | None] = mapped_column(String(80))
    expiry_date: Mapped[date | None] = mapped_column(Date)
    file_name: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    booking = relationship("TravelBooking", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
