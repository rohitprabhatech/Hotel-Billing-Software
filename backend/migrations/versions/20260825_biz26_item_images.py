"""Item images metadata (BIZ-26).

Revision ID: 20260825_biz26_item_images
Revises: 20260825_biz25_item_variants
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz26_item_images"
down_revision = "20260825_biz25_item_variants"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("item_images"):
        return
    op.create_table(
        "item_images",
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
        sa.Column(
            "variant_id",
            sa.String(36),
            sa.ForeignKey("item_variants.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("storage_key", sa.String(80), nullable=True),
        sa.Column("alt_text", sa.String(120), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_item_images_tenant_id", "item_images", ["tenant_id"])
    op.create_index("ix_item_images_item_id", "item_images", ["item_id"])
    op.create_index("ix_item_images_variant_id", "item_images", ["variant_id"])


def downgrade() -> None:
    if not _has_table("item_images"):
        return
    op.drop_index("ix_item_images_variant_id", table_name="item_images")
    op.drop_index("ix_item_images_item_id", table_name="item_images")
    op.drop_index("ix_item_images_tenant_id", table_name="item_images")
    op.drop_table("item_images")
