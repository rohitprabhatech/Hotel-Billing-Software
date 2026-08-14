"""Bill delivery attempts (WhatsApp, etc.) — separate from financial bill status."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class BillDelivery(db.Model, TimestampMixin):
    __tablename__ = "bill_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    delivery_method: Mapped[str] = mapped_column(String(20), nullable=False)  # WHATSAPP
    recipient_phone_e164: Mapped[str | None] = mapped_column(String(20))
    recipient_phone_masked: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    provider_message_id: Mapped[str | None] = mapped_column(String(120), index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
    attempted_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL")
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )
