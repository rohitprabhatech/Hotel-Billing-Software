"""F&B reports and wastage entries (BIZ-18).

Revision ID: 20260822_biz18_fb_reports_wastage
Revises: 20260822_biz17_cafe_addons_combos
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz18_fb_reports_wastage"
down_revision = "20260822_biz17_cafe_addons_combos"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("wastage_entries"):
        return

    op.create_table(
        "wastage_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("wastage_date", sa.Date(), nullable=False),
        sa.Column("stock_movement_id", sa.String(36), sa.ForeignKey("stock_movements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_wastage_entries_tenant_id", "wastage_entries", ["tenant_id"])
    op.create_index("ix_wastage_entries_item_id", "wastage_entries", ["item_id"])
    op.create_index("ix_wastage_entries_wastage_date", "wastage_entries", ["wastage_date"])
    op.create_index("ix_wastage_entries_stock_movement_id", "wastage_entries", ["stock_movement_id"])


def downgrade() -> None:
    if _has_table("wastage_entries"):
        op.drop_index("ix_wastage_entries_stock_movement_id", table_name="wastage_entries")
        op.drop_index("ix_wastage_entries_wastage_date", table_name="wastage_entries")
        op.drop_index("ix_wastage_entries_item_id", table_name="wastage_entries")
        op.drop_index("ix_wastage_entries_tenant_id", table_name="wastage_entries")
        op.drop_table("wastage_entries")
