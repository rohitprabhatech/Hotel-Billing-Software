"""Production runs for bakery finished-goods manufacture (BIZ-40)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class ProductionRunNumberCounter(db.Model):
    __tablename__ = "production_run_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ProductionRun(db.Model, TimestampMixin):
    __tablename__ = "production_runs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "run_number", name="uq_production_runs_tenant_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    run_number: Mapped[str] = mapped_column(String(30), nullable=False)
    recipe_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recipes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    finished_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    finished_item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    run_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    finished_stock_movement_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("stock_movements.id", ondelete="SET NULL"), index=True
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    recipe = relationship("Recipe", foreign_keys=[recipe_id])
    finished_item = relationship("Item", foreign_keys=[finished_item_id])
    finished_stock_movement = relationship(
        "StockMovement", foreign_keys=[finished_stock_movement_id]
    )
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship(
        "ProductionRunItem",
        back_populates="production_run",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ProductionRunItem.sort_order",
    )


class ProductionRunItem(db.Model):
    __tablename__ = "production_run_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    production_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("production_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    uom: Mapped[str | None] = mapped_column(String(16))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_movement_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("stock_movements.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    production_run = relationship("ProductionRun", back_populates="items")
    item = relationship("Item", foreign_keys=[item_id])
    stock_movement = relationship("StockMovement", foreign_keys=[stock_movement_id])
