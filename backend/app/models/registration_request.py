"""Public business registration request — pending Master Admin approval."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

REGISTRATION_PENDING = "PENDING"
REGISTRATION_APPROVED = "APPROVED"
REGISTRATION_REJECTED = "REJECTED"
REGISTRATION_STATUSES = {
    REGISTRATION_PENDING,
    REGISTRATION_APPROVED,
    REGISTRATION_REJECTED,
}


class RegistrationRequest(db.Model, TimestampMixin):
    __tablename__ = "registration_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[str] = mapped_column(String(40), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(80))
    pincode: Mapped[str | None] = mapped_column(String(20))
    gst_number: Mapped[str | None] = mapped_column(String(30))
    fssai_number: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=REGISTRATION_PENDING)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    approved_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("master_admins.id", ondelete="SET NULL")
    )
    rejected_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("master_admins.id", ondelete="SET NULL")
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="SET NULL")
    )
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    tenant = relationship("Tenant", foreign_keys=[tenant_id])
