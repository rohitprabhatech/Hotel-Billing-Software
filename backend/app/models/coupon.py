"""Cafe coupon models (Sprint 5)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

DISCOUNT_PERCENT = "percent"
DISCOUNT_AMOUNT = "amount"
ALLOWED_DISCOUNT_TYPES = frozenset({DISCOUNT_PERCENT, DISCOUNT_AMOUNT})


class Coupon(db.Model, TimestampMixin):
    __tablename__ = "coupons"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_coupons_tenant_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    discount_type: Mapped[str] = mapped_column(String(16), nullable=False, default=DISCOUNT_AMOUNT)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_order_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    max_discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    starts_on: Mapped[date | None] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    usage_limit: Mapped[int | None] = mapped_column(Integer)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    redemptions = relationship(
        "CouponRedemption", back_populates="coupon", lazy="selectin", cascade="all, delete-orphan"
    )


class CouponRedemption(db.Model):
    __tablename__ = "coupon_redemptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    coupon_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("coupons.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="SET NULL"), index=True
    )
    order_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    discount_applied: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    redeemed_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    coupon = relationship("Coupon", back_populates="redemptions")
