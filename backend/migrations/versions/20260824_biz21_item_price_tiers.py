"""Item price tiers for bulk pricing (BIZ-21).

Revision ID: 20260824_biz21_item_price_tiers
Revises: 20260822_biz18_fb_reports_wastage
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260824_biz21_item_price_tiers"
down_revision = "20260822_biz18_fb_reports_wastage"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("item_price_tiers"):
        return

    op.create_table(
        "item_price_tiers",
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
        sa.Column("min_quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint(
            "tenant_id",
            "item_id",
            "min_quantity",
            name="uq_item_price_tiers_tenant_item_min_qty",
        ),
    )
    op.create_index("ix_item_price_tiers_tenant_id", "item_price_tiers", ["tenant_id"])
    op.create_index("ix_item_price_tiers_item_id", "item_price_tiers", ["item_id"])


def downgrade() -> None:
    if _has_table("item_price_tiers"):
        op.drop_index("ix_item_price_tiers_item_id", table_name="item_price_tiers")
        op.drop_index("ix_item_price_tiers_tenant_id", table_name="item_price_tiers")
        op.drop_table("item_price_tiers")
