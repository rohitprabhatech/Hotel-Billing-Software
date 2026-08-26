"""BIZ-47: furniture product attributes on items (dimensions / material / color).

Revision ID: 20260826_biz47_furniture_product_attributes
Revises: 20260826_biz45_book_store_metadata
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz47_furniture_product_attributes"
down_revision = "20260826_biz45_book_store_metadata"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "dimension_length"):
        op.add_column("items", sa.Column("dimension_length", sa.Numeric(12, 3), nullable=True))
    if not _has_column("items", "dimension_width"):
        op.add_column("items", sa.Column("dimension_width", sa.Numeric(12, 3), nullable=True))
    if not _has_column("items", "dimension_height"):
        op.add_column("items", sa.Column("dimension_height", sa.Numeric(12, 3), nullable=True))
    if not _has_column("items", "material"):
        op.add_column("items", sa.Column("material", sa.String(120), nullable=True))
    if not _has_column("items", "color"):
        op.add_column("items", sa.Column("color", sa.String(80), nullable=True))
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    if "ix_items_tenant_material" not in indexes:
        op.create_index("ix_items_tenant_material", "items", ["tenant_id", "material"])


def downgrade() -> None:
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    if "ix_items_tenant_material" in indexes:
        op.drop_index("ix_items_tenant_material", table_name="items")
    for col in ("color", "material", "dimension_height", "dimension_width", "dimension_length"):
        if _has_column("items", col):
            op.drop_column("items", col)
