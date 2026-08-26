"""BIZ-32: mobile catalog brand/model fields on items.

Revision ID: 20260825_biz32_mobile_brand_model
Revises: 20260825_biz31_repairs_serial_exchange
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz32_mobile_brand_model"
down_revision = "20260825_biz31_repairs_serial_exchange"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "brand"):
        op.add_column("items", sa.Column("brand", sa.String(80), nullable=True))
    if not _has_column("items", "model_name"):
        op.add_column("items", sa.Column("model_name", sa.String(120), nullable=True))
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    if "ix_items_tenant_brand" not in indexes:
        op.create_index("ix_items_tenant_brand", "items", ["tenant_id", "brand"])


def downgrade() -> None:
    bind = op.get_bind()
    indexes = {row["name"] for row in inspect(bind).get_indexes("items")}
    if "ix_items_tenant_brand" in indexes:
        op.drop_index("ix_items_tenant_brand", table_name="items")
    if _has_column("items", "model_name"):
        op.drop_column("items", "model_name")
    if _has_column("items", "brand"):
        op.drop_column("items", "brand")
