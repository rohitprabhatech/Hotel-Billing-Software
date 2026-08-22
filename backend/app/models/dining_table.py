"""Tenant-scoped dining table (BIZ-12)."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.tables import TABLE_STATUS_AVAILABLE
from app.extensions import db
from app.models.base import TimestampMixin


class DiningTable(db.Model, TimestampMixin):
    __tablename__ = "dining_tables"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_dining_tables_tenant_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    section: Mapped[str | None] = mapped_column(String(64))
    capacity: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=TABLE_STATUS_AVAILABLE)
    merged_into_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("dining_tables.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    merged_into = relationship(
        "DiningTable",
        remote_side="DiningTable.id",
        foreign_keys=[merged_into_id],
        back_populates="merged_children",
    )
    merged_children = relationship(
        "DiningTable",
        foreign_keys=[merged_into_id],
        back_populates="merged_into",
        lazy="selectin",
    )
