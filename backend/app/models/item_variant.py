"""Item size/color/brand variants (BIZ-25)."""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class ItemVariant(db.Model, TimestampMixin):
    __tablename__ = "item_variants"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "item_id",
            "size",
            "color",
            name="uq_item_variants_tenant_item_size_color",
        ),
        UniqueConstraint("tenant_id", "sku", name="uq_item_variants_tenant_sku"),
        UniqueConstraint("tenant_id", "barcode", name="uq_item_variants_tenant_barcode"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    size: Mapped[str] = mapped_column(String(32), nullable=False)
    color: Mapped[str] = mapped_column(String(64), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80))
    sku: Mapped[str | None] = mapped_column(String(64))
    barcode: Mapped[str | None] = mapped_column(String(64), index=True)
    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    item = relationship("Item", back_populates="variants")
