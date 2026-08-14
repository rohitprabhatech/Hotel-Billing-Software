"""Per-tenant WhatsApp Cloud API configuration."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.base import TimestampMixin


class TenantWhatsappConfig(db.Model, TimestampMixin):
    __tablename__ = "tenant_whatsapp_configs"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    phone_number_id: Mapped[str | None] = mapped_column(String(64))
    waba_id: Mapped[str | None] = mapped_column(String(64))
    display_phone_e164: Mapped[str | None] = mapped_column(String(20))
    access_token_encrypted: Mapped[str | None] = mapped_column(Text)
    template_name: Mapped[str | None] = mapped_column(String(120))
    template_language: Mapped[str] = mapped_column(String(20), nullable=False, default="en")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
