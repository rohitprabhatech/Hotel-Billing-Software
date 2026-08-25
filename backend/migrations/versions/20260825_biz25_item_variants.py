"""Item variants (size/color/brand) and bill line variant_id (BIZ-25).

Revision ID: 20260825_biz25_item_variants
Revises: 20260824_biz22_item_batches
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz25_item_variants"
down_revision = "20260824_biz22_item_batches"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    cols = [row["name"] for row in inspect(bind).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "tracks_variants"):
        op.add_column(
            "items",
            sa.Column("tracks_variants", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if not _has_table("item_variants"):
        op.create_table(
            "item_variants",
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
            sa.Column("size", sa.String(32), nullable=False),
            sa.Column("color", sa.String(64), nullable=False),
            sa.Column("brand", sa.String(80), nullable=True),
            sa.Column("sku", sa.String(64), nullable=True),
            sa.Column("barcode", sa.String(64), nullable=True),
            sa.Column("stock_quantity", sa.Numeric(12, 3), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id",
                "item_id",
                "size",
                "color",
                name="uq_item_variants_tenant_item_size_color",
            ),
            sa.UniqueConstraint("tenant_id", "sku", name="uq_item_variants_tenant_sku"),
            sa.UniqueConstraint("tenant_id", "barcode", name="uq_item_variants_tenant_barcode"),
        )
        op.create_index("ix_item_variants_tenant_id", "item_variants", ["tenant_id"])
        op.create_index("ix_item_variants_item_id", "item_variants", ["item_id"])
        op.create_index("ix_item_variants_barcode", "item_variants", ["barcode"])

    if not _has_column("bill_items", "variant_id"):
        op.add_column(
            "bill_items",
            sa.Column(
                "variant_id",
                sa.String(36),
                sa.ForeignKey("item_variants.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("ix_bill_items_variant_id", "bill_items", ["variant_id"])


def downgrade() -> None:
    if _has_column("bill_items", "variant_id"):
        op.drop_index("ix_bill_items_variant_id", table_name="bill_items")
        op.drop_column("bill_items", "variant_id")
    if _has_table("item_variants"):
        op.drop_index("ix_item_variants_barcode", table_name="item_variants")
        op.drop_index("ix_item_variants_item_id", table_name="item_variants")
        op.drop_index("ix_item_variants_tenant_id", table_name="item_variants")
        op.drop_table("item_variants")
    if _has_column("items", "tracks_variants"):
        op.drop_column("items", "tracks_variants")
