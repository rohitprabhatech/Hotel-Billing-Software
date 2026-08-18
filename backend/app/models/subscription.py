"""Tenant SaaS subscription / trial entitlement."""

from datetime import datetime

from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin

SUBSCRIPTION_TRIAL = "TRIAL"
SUBSCRIPTION_ACTIVE = "ACTIVE"
SUBSCRIPTION_EXPIRING = "EXPIRING"
SUBSCRIPTION_EXPIRED = "EXPIRED"
SUBSCRIPTION_CANCELLED = "CANCELLED"
SUBSCRIPTION_SUSPENDED = "SUSPENDED"
SUBSCRIPTION_STATUSES = {
    SUBSCRIPTION_TRIAL,
    SUBSCRIPTION_ACTIVE,
    SUBSCRIPTION_EXPIRING,
    SUBSCRIPTION_EXPIRED,
    SUBSCRIPTION_CANCELLED,
    SUBSCRIPTION_SUSPENDED,
}
ACCESS_STATUSES = {
    SUBSCRIPTION_TRIAL,
    SUBSCRIPTION_ACTIVE,
    SUBSCRIPTION_EXPIRING,
}
PAYMENT_COMPLIMENTARY = "COMPLIMENTARY"
PAYMENT_MANUAL = "MANUAL"


class Subscription(db.Model, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plan_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("subscription_plans.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=SUBSCRIPTION_TRIAL)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    trial_starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    price_at_purchase: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    payment_status: Mapped[str | None] = mapped_column(String(30))
    payment_provider: Mapped[str | None] = mapped_column(String(40))
    payment_reference: Mapped[str | None] = mapped_column(String(120))

    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
