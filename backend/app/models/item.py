"""Tenant-scoped catalog item model."""

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class Item(db.Model, TimestampMixin):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_items_tenant_name"),
        UniqueConstraint("tenant_id", "sku", name="uq_items_tenant_sku"),
        UniqueConstraint("tenant_id", "barcode", name="uq_items_tenant_barcode"),
        UniqueConstraint("tenant_id", "isbn", name="uq_items_tenant_isbn"),
        Index("ix_items_tenant_active_name", "tenant_id", "is_active", "name"),
        CheckConstraint(
            "stock_quantity IS NULL OR stock_quantity >= 0",
            name="chk_items_stock",
        ),
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
    barcode: Mapped[str | None] = mapped_column(String(64), index=True)
    uom: Mapped[str] = mapped_column(String(16), nullable=False, default="pcs")
    sale_uom: Mapped[str | None] = mapped_column(String(16))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gst_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )
    stock_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    minimum_stock_level: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_menu: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_veg: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tracks_batches: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    block_expired_batches: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tracks_variants: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tracks_serial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(120))
    isbn: Mapped[str | None] = mapped_column(String(32))
    author: Mapped[str | None] = mapped_column(String(160), index=True)
    publisher: Mapped[str | None] = mapped_column(String(160))
    dimension_length: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    dimension_width: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    dimension_height: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    material: Mapped[str | None] = mapped_column(String(120))
    color: Mapped[str | None] = mapped_column(String(80))

    category = relationship("Category", back_populates="items")
    creator = relationship("User", foreign_keys=[created_by])
    price_tiers = relationship(
        "ItemPriceTier",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemPriceTier.min_quantity",
    )
    batches = relationship(
        "ItemBatch",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemBatch.expiry_date",
    )
    variants = relationship(
        "ItemVariant",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemVariant.size, ItemVariant.color",
    )
    images = relationship(
        "ItemImage",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemImage.sort_order",
    )
    serial_units = relationship(
        "SerialUnit",
        back_populates="item",
        cascade="all, delete-orphan",
    )
    accessory_links = relationship(
        "ItemAccessory",
        foreign_keys="ItemAccessory.item_id",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemAccessory.sort_order",
    )
