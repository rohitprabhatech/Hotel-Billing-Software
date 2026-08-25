"""Related accessory items for a primary product (BIZ-30)."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class ItemAccessory(db.Model, TimestampMixin):
    __tablename__ = "item_accessories"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "item_id",
            "accessory_item_id",
            name="uq_item_accessories_tenant_item_accessory",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    accessory_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    item = relationship("Item", foreign_keys=[item_id], back_populates="accessory_links")
    accessory = relationship("Item", foreign_keys=[accessory_item_id])
