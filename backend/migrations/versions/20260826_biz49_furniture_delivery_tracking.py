"""BIZ-49: furniture delivery jobs + installation custom-order link.

Revision ID: 20260826_biz49_furniture_delivery_tracking
Revises: 20260826_biz47_furniture_product_attributes
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz49_furniture_delivery_tracking"
down_revision = "20260826_biz47_furniture_product_attributes"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_table("delivery_jobs"):
        op.create_table(
            "delivery_jobs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("delivery_number", sa.String(50), nullable=False),
            sa.Column("delivery_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "custom_order_id",
                sa.String(36),
                sa.ForeignKey("custom_product_orders.id", ondelete="RESTRICT"),
                nullable=True,
            ),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("delivery_address", sa.Text(), nullable=True),
            sa.Column("scheduled_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="SCHEDULED"),
            sa.Column("driver_name", sa.String(120), nullable=True),
            sa.Column("vehicle_number", sa.String(40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("out_for_delivery_at", sa.DateTime(), nullable=True),
            sa.Column("delivered_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id", "delivery_number", name="uq_delivery_jobs_tenant_number"
            ),
        )
        op.create_index("ix_delivery_jobs_tenant_id", "delivery_jobs", ["tenant_id"])
        op.create_index("ix_delivery_jobs_custom_order_id", "delivery_jobs", ["custom_order_id"])
        op.create_index("ix_delivery_jobs_status", "delivery_jobs", ["tenant_id", "status"])
        op.create_index(
            "ix_delivery_jobs_scheduled_at", "delivery_jobs", ["tenant_id", "scheduled_at"]
        )

    if not _has_table("delivery_number_counters"):
        op.create_table(
            "delivery_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if _has_table("installation_orders"):
        if _has_column("installation_orders", "serial_unit_id"):
            op.alter_column(
                "installation_orders",
                "serial_unit_id",
                existing_type=sa.String(36),
                nullable=True,
            )
        if _has_column("installation_orders", "item_id"):
            op.alter_column(
                "installation_orders",
                "item_id",
                existing_type=sa.String(36),
                nullable=True,
            )
        if not _has_column("installation_orders", "custom_order_id"):
            op.add_column(
                "installation_orders",
                sa.Column(
                    "custom_order_id",
                    sa.String(36),
                    sa.ForeignKey("custom_product_orders.id", ondelete="RESTRICT"),
                    nullable=True,
                ),
            )
            op.create_index(
                "ix_installation_orders_custom_order_id",
                "installation_orders",
                ["custom_order_id"],
            )


def downgrade() -> None:
    if _has_table("installation_orders") and _has_column("installation_orders", "custom_order_id"):
        op.drop_index("ix_installation_orders_custom_order_id", table_name="installation_orders")
        op.drop_column("installation_orders", "custom_order_id")
    if _has_table("delivery_jobs"):
        op.drop_table("delivery_jobs")
    if _has_table("delivery_number_counters"):
        op.drop_table("delivery_number_counters")
