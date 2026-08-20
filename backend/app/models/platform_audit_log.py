"""Platform-wide audit log for Master Admin actions (not tenant-scoped)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import utcnow

ACTION_BUSINESS_APPROVED = "BUSINESS_APPROVED"
ACTION_BUSINESS_REJECTED = "BUSINESS_REJECTED"
ACTION_BUSINESS_ACTIVATED = "BUSINESS_ACTIVATED"
ACTION_BUSINESS_DEACTIVATED = "BUSINESS_DEACTIVATED"
ACTION_BUSINESS_SUSPENDED = "BUSINESS_SUSPENDED"
ACTION_BUSINESS_UNSUSPENDED = "BUSINESS_UNSUSPENDED"
ACTION_PLAN_CREATED = "PLAN_CREATED"
ACTION_PLAN_UPDATED = "PLAN_UPDATED"
ACTION_PLAN_ACTIVATED = "PLAN_ACTIVATED"
ACTION_PLAN_DEACTIVATED = "PLAN_DEACTIVATED"
ACTION_TRIAL_SETTINGS_UPDATED = "TRIAL_SETTINGS_UPDATED"
ACTION_SUBSCRIPTION_UPDATED = "SUBSCRIPTION_UPDATED"


class PlatformAuditLog(db.Model):
    __tablename__ = "platform_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("master_admins.id", ondelete="SET NULL"), index=True
    )
    actor_name: Mapped[str | None] = mapped_column(String(120))
    actor_email: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36))
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="SET NULL"), index=True
    )
    old_data: Mapped[dict | None] = mapped_column(JSON)
    new_data: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        default=utcnow,
        index=True,
    )

    actor = relationship("MasterAdmin", foreign_keys=[actor_id])
