"""Idempotency log for subscription expiry notices (one per period)."""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin

NOTICE_EXPIRING = "EXPIRING"
NOTICE_EXPIRED = "EXPIRED"
NOTICE_TYPES = {NOTICE_EXPIRING, NOTICE_EXPIRED}


class SubscriptionNotice(db.Model, TimestampMixin):
    __tablename__ = "subscription_notices"
    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "notice_type",
            "period_key",
            name="uq_subscription_notices_period",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subscription_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("subscriptions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    notice_type: Mapped[str] = mapped_column(String(20), nullable=False)
    period_key: Mapped[str] = mapped_column(String(32), nullable=False)

    subscription = relationship("Subscription", foreign_keys=[subscription_id])
