"""Add kots and kot_items (BIZ-14).

Revision ID: 20260822_biz14_kots
Revises: 20260822_biz13_orders
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz14_kots"
down_revision = "20260822_biz13_orders"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("kot_number_counters"):
        op.create_table(
            "kot_number_counters",
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if _has_table("kots"):
        return

    op.create_table(
        "kots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kot_number", sa.String(50), nullable=False),
        sa.Column("kot_sequence", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="queued"),
        sa.Column("channel", sa.String(16), nullable=False),
        sa.Column("dining_table_id", sa.String(36), sa.ForeignKey("dining_tables.id", ondelete="SET NULL"), nullable=True),
        sa.Column("dining_table_code", sa.String(32), nullable=True),
        sa.Column("order_number", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("print_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("printed_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "kot_number", name="uq_kots_tenant_number"),
        sa.UniqueConstraint("tenant_id", "kot_sequence", name="uq_kots_tenant_sequence"),
    )
    op.create_index("ix_kots_tenant_id", "kots", ["tenant_id"])
    op.create_index("ix_kots_order_id", "kots", ["order_id"])
    op.create_index("ix_kots_dining_table_id", "kots", ["dining_table_id"])

    op.create_table(
        "kot_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kot_id", sa.String(36), sa.ForeignKey("kots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_item_id", sa.String(36), sa.ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_kot_items_tenant_id", "kot_items", ["tenant_id"])
    op.create_index("ix_kot_items_kot_id", "kot_items", ["kot_id"])
    op.create_index("ix_kot_items_order_item_id", "kot_items", ["order_item_id"])


def downgrade() -> None:
    if _has_table("kot_items"):
        op.drop_index("ix_kot_items_order_item_id", table_name="kot_items")
        op.drop_index("ix_kot_items_kot_id", table_name="kot_items")
        op.drop_index("ix_kot_items_tenant_id", table_name="kot_items")
        op.drop_table("kot_items")
    if _has_table("kots"):
        op.drop_index("ix_kots_dining_table_id", table_name="kots")
        op.drop_index("ix_kots_order_id", table_name="kots")
        op.drop_index("ix_kots_tenant_id", table_name="kots")
        op.drop_table("kots")
    if _has_table("kot_number_counters"):
        op.drop_table("kot_number_counters")
