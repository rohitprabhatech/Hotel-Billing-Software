"""BIZ-45: book metadata fields on items (ISBN / author / publisher).

Revision ID: 20260826_biz45_book_store_metadata
Revises: 20260825_biz42_custom_product_orders
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz45_book_store_metadata"
down_revision = "20260825_biz42_custom_product_orders"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "isbn"):
        op.add_column("items", sa.Column("isbn", sa.String(32), nullable=True))
    if not _has_column("items", "author"):
        op.add_column("items", sa.Column("author", sa.String(160), nullable=True))
    if not _has_column("items", "publisher"):
        op.add_column("items", sa.Column("publisher", sa.String(160), nullable=True))
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    uniques = {row["name"] for row in inspect(bind).get_unique_constraints("items")}
    if "uq_items_tenant_isbn" not in uniques and "uq_items_tenant_isbn" not in indexes:
        op.create_unique_constraint("uq_items_tenant_isbn", "items", ["tenant_id", "isbn"])
    if "ix_items_tenant_author" not in indexes:
        op.create_index("ix_items_tenant_author", "items", ["tenant_id", "author"])


def downgrade() -> None:
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    uniques = {row["name"] for row in inspect(bind).get_unique_constraints("items")}
    if "ix_items_tenant_author" in indexes:
        op.drop_index("ix_items_tenant_author", table_name="items")
    if "uq_items_tenant_isbn" in uniques:
        op.drop_constraint("uq_items_tenant_isbn", "items", type_="unique")
    if _has_column("items", "publisher"):
        op.drop_column("items", "publisher")
    if _has_column("items", "author"):
        op.drop_column("items", "author")
    if _has_column("items", "isbn"):
        op.drop_column("items", "isbn")
