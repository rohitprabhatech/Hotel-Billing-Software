"""BIZ-33: installation orders linked to serial sales.

Revision ID: 20260825_biz33_installation_orders
Revises: 20260825_biz32_mobile_brand_model
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz33_installation_orders"
down_revision = "20260825_biz32_mobile_brand_model"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("installation_orders"):
        op.create_table(
            "installation_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("installation_number", sa.String(50), nullable=False),
            sa.Column("installation_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "serial_unit_id",
                sa.String(36),
                sa.ForeignKey("serial_units.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("install_address", sa.Text(), nullable=True),
            sa.Column("scheduled_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="SCHEDULED"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("technician_name", sa.String(120), nullable=True),
            sa.Column("estimated_charge", sa.Numeric(12, 2), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id",
                "installation_number",
                name="uq_installation_orders_tenant_number",
            ),
        )
        op.create_index("ix_installation_orders_tenant_id", "installation_orders", ["tenant_id"])
        op.create_index(
            "ix_installation_orders_serial_unit_id", "installation_orders", ["serial_unit_id"]
        )
        op.create_index("ix_installation_orders_item_id", "installation_orders", ["item_id"])
        op.create_index("ix_installation_orders_bill_id", "installation_orders", ["bill_id"])
        op.create_index(
            "ix_installation_orders_status", "installation_orders", ["tenant_id", "status"]
        )
        op.create_index(
            "ix_installation_orders_scheduled_at",
            "installation_orders",
            ["tenant_id", "scheduled_at"],
        )

    if not _has_table("installation_number_counters"):
        op.create_table(
            "installation_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )


def downgrade() -> None:
    if _has_table("installation_orders"):
        op.drop_table("installation_orders")
    if _has_table("installation_number_counters"):
        op.drop_table("installation_number_counters")
