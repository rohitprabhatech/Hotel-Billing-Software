"""Tour packages for travel agencies (BIZ-56) — service catalog, not stock SKUs."""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class TourPackage(db.Model, TimestampMixin):
    __tablename__ = "tour_packages"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_tour_packages_tenant_code"),
        UniqueConstraint("tenant_id", "item_id", name="uq_tour_packages_tenant_item"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    destination: Mapped[str | None] = mapped_column(String(160))
    transport_type: Mapped[str | None] = mapped_column(String(60))
    duration_days: Mapped[int | None] = mapped_column(Integer)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )
    # Linked untracked catalog item for billing (stock_quantity always NULL).
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    item = relationship("Item", foreign_keys=[item_id])
    creator = relationship("User", foreign_keys=[created_by])
