"""Add orders and order_items (BIZ-13).

Revision ID: 20260822_biz13_orders
Revises: 20260822_biz12_dining_tables
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz13_orders"
down_revision = "20260822_biz12_dining_tables"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("order_number_counters"):
        op.create_table(
            "order_number_counters",
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if _has_table("orders"):
        return

    op.create_table(
        "orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("order_number", sa.String(50), nullable=False),
        sa.Column("order_sequence", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False, server_default="dine_in"),
        sa.Column("status", sa.String(16), nullable=False, server_default="OPEN"),
        sa.Column("dining_table_id", sa.String(36), sa.ForeignKey("dining_tables.id", ondelete="SET NULL"), nullable=True),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("customer_name", sa.String(120), nullable=True),
        sa.Column("customer_phone_country_code", sa.String(8), nullable=True),
        sa.Column("customer_phone_national", sa.String(20), nullable=True),
        sa.Column("customer_phone_e164", sa.String(20), nullable=True),
        sa.Column("delivery_address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("gst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("grand_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("bill_id", sa.String(36), sa.ForeignKey("bills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cancelled_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "order_number", name="uq_orders_tenant_number"),
        sa.UniqueConstraint("tenant_id", "order_sequence", name="uq_orders_tenant_sequence"),
    )
    op.create_index("ix_orders_tenant_id", "orders", ["tenant_id"])
    op.create_index("ix_orders_dining_table_id", "orders", ["dining_table_id"])
    op.create_index("ix_orders_bill_id", "orders", ["bill_id"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("gst_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_order_items_tenant_id", "order_items", ["tenant_id"])
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    if _has_table("order_items"):
        op.drop_index("ix_order_items_order_id", table_name="order_items")
        op.drop_index("ix_order_items_tenant_id", table_name="order_items")
        op.drop_table("order_items")
    if _has_table("orders"):
        op.drop_index("ix_orders_bill_id", table_name="orders")
        op.drop_index("ix_orders_dining_table_id", table_name="orders")
        op.drop_index("ix_orders_tenant_id", table_name="orders")
        op.drop_table("orders")
    if _has_table("order_number_counters"):
        op.drop_table("order_number_counters")
