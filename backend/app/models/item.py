"""Tenant-scoped catalog item model."""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class Item(db.Model, TimestampMixin):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_items_tenant_name"),
        UniqueConstraint("tenant_id", "sku", name="uq_items_tenant_sku"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gst_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )
    stock_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    minimum_stock_level: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category = relationship("Category", back_populates="items")
    creator = relationship("User", foreign_keys=[created_by])
