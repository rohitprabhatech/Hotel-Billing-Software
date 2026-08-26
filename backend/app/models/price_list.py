"""Wholesale price lists and customer assignments (BIZ-51)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow

LIST_TYPE_WHOLESALE = "WHOLESALE"
LIST_TYPE_RETAIL = "RETAIL"

ALLOWED_LIST_TYPES = frozenset({LIST_TYPE_WHOLESALE, LIST_TYPE_RETAIL})


class PriceList(db.Model, TimestampMixin):
    __tablename__ = "price_lists"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_price_lists_tenant_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    list_type: Mapped[str] = mapped_column(String(20), nullable=False, default=LIST_TYPE_WHOLESALE)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)

    items = relationship("PriceListItem", back_populates="price_list", lazy="selectin")
    customer_assignments = relationship(
        "CustomerPriceList", back_populates="price_list", lazy="dynamic"
    )


class PriceListItem(db.Model, TimestampMixin):
    __tablename__ = "price_list_items"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "price_list_id",
            "item_id",
            name="uq_price_list_items_tenant_list_item",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    price_list_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("price_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    price_list = relationship("PriceList", back_populates="items")
    item = relationship("Item", foreign_keys=[item_id])


class CustomerPriceList(db.Model, TimestampMixin):
    __tablename__ = "customer_price_lists"
    __table_args__ = (
        UniqueConstraint("tenant_id", "customer_id", name="uq_customer_price_lists_tenant_customer"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price_list_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("price_lists.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    customer = relationship("Customer", foreign_keys=[customer_id])
    price_list = relationship("PriceList", back_populates="customer_assignments")
