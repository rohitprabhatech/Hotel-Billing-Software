"""Tenant-scoped category model (optional parent for subcategory)."""

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin


class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "parent_id", "name", name="uq_categories_tenant_parent_name"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="RESTRICT")
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent = relationship("Category", remote_side=[id], backref="children")
    items = relationship("Item", back_populates="category", lazy="dynamic")