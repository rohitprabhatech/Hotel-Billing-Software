"""BIZ-31: repair orders, serial quarantine, return/exchange serial fields.

Revision ID: 20260825_biz31_repairs_serial_exchange
Revises: 20260825_biz30_warranty_accessories
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision = "20260825_biz31_repairs_serial_exchange"
down_revision = "20260825_biz30_warranty_accessories"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_table("repair_orders"):
        op.create_table(
            "repair_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("repair_number", sa.String(50), nullable=False),
            sa.Column("repair_sequence", sa.Integer(), nullable=False),
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
            sa.Column("issue_description", sa.Text(), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="RECEIVED"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("estimated_charge", sa.Numeric(12, 2), nullable=True),
            sa.Column("delivered_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "repair_number", name="uq_repair_orders_tenant_number"),
        )
        op.create_index("ix_repair_orders_tenant_id", "repair_orders", ["tenant_id"])
        op.create_index("ix_repair_orders_serial_unit_id", "repair_orders", ["serial_unit_id"])
        op.create_index("ix_repair_orders_item_id", "repair_orders", ["item_id"])
        op.create_index("ix_repair_orders_bill_id", "repair_orders", ["bill_id"])
        op.create_index("ix_repair_orders_status", "repair_orders", ["tenant_id", "status"])

    if not _has_table("repair_number_counters"):
        op.create_table(
            "repair_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if not _has_column("sales_return_items", "serial_unit_id"):
        op.add_column(
            "sales_return_items",
            sa.Column(
                "serial_unit_id",
                sa.String(36),
                sa.ForeignKey("serial_units.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
    if not _has_column("sales_return_items", "exchange_serial_unit_id"):
        op.add_column(
            "sales_return_items",
            sa.Column(
                "exchange_serial_unit_id",
                sa.String(36),
                sa.ForeignKey("serial_units.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
    if not _has_column("sales_return_items", "quarantine"):
        op.add_column(
            "sales_return_items",
            sa.Column("quarantine", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    # Expand serial status CHECK to allow QUARANTINE (MariaDB/MySQL tolerant drops).
    bind = op.get_bind()
    for stmt in (
        "ALTER TABLE serial_units DROP CONSTRAINT chk_serial_units_status",
        "ALTER TABLE serial_units DROP CHECK chk_serial_units_status",
    ):
        try:
            bind.execute(text(stmt))
            break
        except Exception:
            continue
    try:
        bind.execute(
            text(
                "ALTER TABLE serial_units ADD CONSTRAINT chk_serial_units_status "
                "CHECK (status IN ('IN_STOCK', 'SOLD', 'QUARANTINE'))"
            )
        )
    except Exception:
        pass


def downgrade() -> None:
    if _has_column("sales_return_items", "quarantine"):
        op.drop_column("sales_return_items", "quarantine")
    if _has_column("sales_return_items", "exchange_serial_unit_id"):
        op.drop_column("sales_return_items", "exchange_serial_unit_id")
    if _has_column("sales_return_items", "serial_unit_id"):
        op.drop_column("sales_return_items", "serial_unit_id")
    if _has_table("repair_orders"):
        op.drop_table("repair_orders")
    if _has_table("repair_number_counters"):
        op.drop_table("repair_number_counters")
