"""BIZ-42: shared custom product orders + advance payments.

Revision ID: 20260825_biz42_custom_product_orders
Revises: 20260825_biz40_bakery_production_runs
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz42_custom_product_orders"
down_revision = "20260825_biz40_bakery_production_runs"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("custom_order_number_counters"):
        op.create_table(
            "custom_order_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
        )

    if not _has_table("custom_product_orders"):
        op.create_table(
            "custom_product_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("order_number", sa.String(30), nullable=False),
            sa.Column("order_type", sa.String(20), nullable=False, server_default="bakery"),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("size", sa.String(80), nullable=True),
            sa.Column("flavor", sa.String(120), nullable=True),
            sa.Column("quantity", sa.Numeric(12, 3), nullable=False, server_default="1"),
            sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("advance_paid", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("delivery_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="BOOKED"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("delivered_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id", "order_number", name="uq_custom_product_orders_tenant_number"
            ),
        )
        op.create_index("ix_custom_product_orders_tenant_id", "custom_product_orders", ["tenant_id"])
        op.create_index(
            "ix_custom_product_orders_customer_id", "custom_product_orders", ["customer_id"]
        )
        op.create_index(
            "ix_custom_product_orders_delivery_at", "custom_product_orders", ["delivery_at"]
        )
        op.create_index("ix_custom_product_orders_bill_id", "custom_product_orders", ["bill_id"])
        op.create_index("ix_custom_product_orders_status", "custom_product_orders", ["status"])

    if not _has_table("custom_order_payments"):
        op.create_table(
            "custom_order_payments",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "custom_order_id",
                sa.String(36),
                sa.ForeignKey("custom_product_orders.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("payment_method", sa.String(30), nullable=False, server_default="cash"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index(
            "ix_custom_order_payments_tenant_id", "custom_order_payments", ["tenant_id"]
        )
        op.create_index(
            "ix_custom_order_payments_custom_order_id",
            "custom_order_payments",
            ["custom_order_id"],
        )


def downgrade() -> None:
    if _has_table("custom_order_payments"):
        op.drop_table("custom_order_payments")
    if _has_table("custom_product_orders"):
        op.drop_table("custom_product_orders")
    if _has_table("custom_order_number_counters"):
        op.drop_table("custom_order_number_counters")
