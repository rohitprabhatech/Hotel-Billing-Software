"""Bill and bill line models + per-tenant bill number counter."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
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
from app.models.base import TimestampMixin, utcnow


class BillNumberCounter(db.Model):
    __tablename__ = "bill_number_counters"

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True
    )
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow, onupdate=utcnow
    )


class Bill(db.Model, TimestampMixin):
    __tablename__ = "bills"
    __table_args__ = (
        UniqueConstraint("tenant_id", "bill_number", name="uq_bills_tenant_bill_number"),
        UniqueConstraint("tenant_id", "bill_sequence", name="uq_bills_tenant_bill_sequence"),
        Index("ix_bills_tenant_created_at", "tenant_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bill_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    # Optional bill reference (table / counter / token / customer note).
    # Column name retained as table_number for backward compatibility.
    table_number: Mapped[str | None] = mapped_column(String(30))
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone_country_code: Mapped[str | None] = mapped_column(String(8))
    customer_phone_national: Mapped[str | None] = mapped_column(String(20))
    customer_phone_e164: Mapped[str | None] = mapped_column(String(20))
    customer_email: Mapped[str | None] = mapped_column(String(255))
    customer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    taxable_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    cgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    sgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    gst_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    grand_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    round_off: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="FINALIZED")
    payment_method: Mapped[str] = mapped_column(
        String(20), nullable=False, default="cash"
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    cancelled_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT")
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    printed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    service_charge: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    transport_charge: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    warehouse_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    split_group_id: Mapped[str | None] = mapped_column(String(36), index=True)
    coupon_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    coupon_code: Mapped[str | None] = mapped_column(String(40))
    coupon_discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )

    # selectin (not joined): list endpoints must not pull every line item.
    items = relationship("BillItem", back_populates="bill", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by])
    customer = relationship("Customer", back_populates="bills")
    order = relationship("Order", foreign_keys=[order_id], back_populates="settlement_bills")


class BillItem(db.Model):
    __tablename__ = "bill_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False
    )
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id", ondelete="SET NULL")
    )
    variant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("item_variants.id", ondelete="SET NULL"), index=True
    )
    serial_unit_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "serial_units.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_bill_items_serial_unit_id",
        ),
        index=True,
    )
    serial_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    warranty_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    taxable_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    cgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    sgst_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    bill = relationship("Bill", back_populates="items")