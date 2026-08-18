"""SaaS subscription plans (platform catalog)."""

from decimal import Decimal

from sqlalchemy import Boolean, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin

BILLING_CYCLE_MONTHLY = "MONTHLY"
BILLING_CYCLE_YEARLY = "YEARLY"
BILLING_CYCLES = {BILLING_CYCLE_MONTHLY, BILLING_CYCLE_YEARLY}
DEFAULT_PLAN_ID = "33333333-3333-3333-3333-333333333333"

DEFAULT_PLAN_FEATURES = [
    "Billing",
    "Item & category management",
    "Stock management & low-stock alerts",
    "Sales reports and exports",
    "Bill printing",
    "WhatsApp bill delivery",
    "Email bill delivery",
    "AI business insights (tenant-scoped)",
    "Notifications",
    "Audit logs",
    "Business dashboard",
    "24/7 technical support access",
]


class SubscriptionPlan(db.Model, TimestampMixin):
    __tablename__ = "subscription_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False, default=BILLING_CYCLE_MONTHLY)
    trial_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    features: Mapped[list | None] = mapped_column(JSON)

    subscriptions = relationship("Subscription", back_populates="plan")
