"""Item batches and expiry tracking (BIZ-22).

Revision ID: 20260824_biz22_item_batches
Revises: 20260824_biz21_item_price_tiers
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260824_biz22_item_batches"
down_revision = "20260824_biz21_item_price_tiers"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "tracks_batches"):
        op.add_column(
            "items",
            sa.Column("tracks_batches", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if not _has_column("items", "block_expired_batches"):
        op.add_column(
            "items",
            sa.Column(
                "block_expired_batches",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )

    if not _has_table("item_batches"):
        op.create_table(
            "item_batches",
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
            sa.Column("batch_code", sa.String(64), nullable=True),
            sa.Column("expiry_date", sa.Date(), nullable=True),
            sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id",
                "item_id",
                "batch_code",
                name="uq_item_batches_tenant_item_code",
            ),
        )
        op.create_index("ix_item_batches_tenant_id", "item_batches", ["tenant_id"])
        op.create_index("ix_item_batches_item_id", "item_batches", ["item_id"])
        op.create_index("ix_item_batches_expiry_date", "item_batches", ["expiry_date"])


def downgrade() -> None:
    if _has_table("item_batches"):
        op.drop_index("ix_item_batches_expiry_date", table_name="item_batches")
        op.drop_index("ix_item_batches_item_id", table_name="item_batches")
        op.drop_index("ix_item_batches_tenant_id", table_name="item_batches")
        op.drop_table("item_batches")
    if _has_column("items", "block_expired_batches"):
        op.drop_column("items", "block_expired_batches")
    if _has_column("items", "tracks_batches"):
        op.drop_column("items", "tracks_batches")
