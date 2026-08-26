"""BIZ-52: sales orders and purchase orders.

Revision ID: 20260826_biz52_sales_purchase_orders
Revises: 20260826_biz51_wholesale_price_lists
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz52_sales_purchase_orders"
down_revision = "20260826_biz51_wholesale_price_lists"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("sales_order_number_counters"):
        op.create_table(
            "sales_order_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    if not _has_table("sales_orders"):
        op.create_table(
            "sales_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("order_number", sa.String(50), nullable=False),
            sa.Column("order_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("expected_delivery_date", sa.Date(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
            sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("gst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("grand_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "order_number", name="uq_sales_orders_tenant_number"),
        )
        op.create_index("ix_sales_orders_tenant_id", "sales_orders", ["tenant_id"])
        op.create_index("ix_sales_orders_customer_id", "sales_orders", ["customer_id"])
        op.create_index("ix_sales_orders_bill_id", "sales_orders", ["bill_id"])

    if not _has_table("sales_order_items"):
        op.create_table(
            "sales_order_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "sales_order_id",
                sa.String(36),
                sa.ForeignKey("sales_orders.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("gst_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
            sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("uom", sa.String(16), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_sales_order_items_tenant_id", "sales_order_items", ["tenant_id"])
        op.create_index("ix_sales_order_items_sales_order_id", "sales_order_items", ["sales_order_id"])

    if not _has_table("purchase_order_number_counters"):
        op.create_table(
            "purchase_order_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    if not _has_table("purchase_orders"):
        op.create_table(
            "purchase_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("order_number", sa.String(50), nullable=False),
            sa.Column("order_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "supplier_id",
                sa.String(36),
                sa.ForeignKey("suppliers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("supplier_name", sa.String(120), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("expected_date", sa.Date(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
            sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("grand_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column(
                "purchase_id",
                sa.String(36),
                sa.ForeignKey("purchases.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "tenant_id", "order_number", name="uq_purchase_orders_tenant_number"
            ),
        )
        op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"])
        op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"])
        op.create_index("ix_purchase_orders_purchase_id", "purchase_orders", ["purchase_id"])

    if not _has_table("purchase_order_items"):
        op.create_table(
            "purchase_order_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "purchase_order_id",
                sa.String(36),
                sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
            sa.Column("line_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("uom", sa.String(16), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_purchase_order_items_tenant_id", "purchase_order_items", ["tenant_id"])
        op.create_index(
            "ix_purchase_order_items_purchase_order_id",
            "purchase_order_items",
            ["purchase_order_id"],
        )


def downgrade() -> None:
    for table, indexes in (
        (
            "purchase_order_items",
            ("ix_purchase_order_items_purchase_order_id", "ix_purchase_order_items_tenant_id"),
        ),
        (
            "purchase_orders",
            (
                "ix_purchase_orders_purchase_id",
                "ix_purchase_orders_supplier_id",
                "ix_purchase_orders_tenant_id",
            ),
        ),
        (
            "sales_order_items",
            ("ix_sales_order_items_sales_order_id", "ix_sales_order_items_tenant_id"),
        ),
        (
            "sales_orders",
            ("ix_sales_orders_bill_id", "ix_sales_orders_customer_id", "ix_sales_orders_tenant_id"),
        ),
    ):
        if _has_table(table):
            for index in indexes:
                op.drop_index(index, table_name=table)
            op.drop_table(table)
    if _has_table("purchase_order_number_counters"):
        op.drop_table("purchase_order_number_counters")
    if _has_table("sales_order_number_counters"):
        op.drop_table("sales_order_number_counters")
