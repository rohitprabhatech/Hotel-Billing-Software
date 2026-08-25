"""Serial units and items.tracks_serial (BIZ-29).

Revision ID: 20260825_biz29_serial_units
Revises: 20260825_biz27_sales_returns
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz29_serial_units"
down_revision = "20260825_biz27_sales_returns"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    cols = [row["name"] for row in inspect(bind).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "tracks_serial"):
        op.add_column(
            "items",
            sa.Column("tracks_serial", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if not _has_table("serial_units"):
        op.create_table(
            "serial_units",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("serial", sa.String(64), nullable=False),
            sa.Column("status", sa.String(16), nullable=False, server_default="IN_STOCK"),
            sa.Column(
                "sold_bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "sold_bill_item_id",
                sa.String(36),
                sa.ForeignKey("bill_items.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("sold_at", sa.DateTime(), nullable=True),
            sa.Column("received_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "serial", name="uq_serial_units_tenant_serial"),
        )
        op.create_index("ix_serial_units_tenant_id", "serial_units", ["tenant_id"])
        op.create_index("ix_serial_units_item_id", "serial_units", ["item_id"])
        op.create_index("ix_serial_units_sold_bill_id", "serial_units", ["sold_bill_id"])

    if not _has_column("bill_items", "serial_unit_id"):
        op.add_column(
            "bill_items",
            sa.Column(
                "serial_unit_id",
                sa.String(36),
                sa.ForeignKey("serial_units.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("ix_bill_items_serial_unit_id", "bill_items", ["serial_unit_id"])
    if not _has_column("bill_items", "serial_number"):
        op.add_column("bill_items", sa.Column("serial_number", sa.String(64), nullable=True))


def downgrade() -> None:
    if _has_column("bill_items", "serial_number"):
        op.drop_column("bill_items", "serial_number")
    if _has_column("bill_items", "serial_unit_id"):
        op.drop_index("ix_bill_items_serial_unit_id", table_name="bill_items")
        op.drop_column("bill_items", "serial_unit_id")
    if _has_table("serial_units"):
        op.drop_table("serial_units")
    if _has_column("items", "tracks_serial"):
        op.drop_column("items", "tracks_serial")
