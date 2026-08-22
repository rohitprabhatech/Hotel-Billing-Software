"""Add barcode and uom columns to items (BIZ-08).

Revision ID: 20260822_biz08_barcode_uom
Revises: 20260822_biz07_expenses
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz08_barcode_uom"
down_revision = "20260822_biz07_expenses"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    return column in {col["name"] for col in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("items", "barcode"):
        op.add_column("items", sa.Column("barcode", sa.String(64), nullable=True))
    if not _has_column("items", "uom"):
        op.add_column(
            "items",
            sa.Column("uom", sa.String(16), nullable=False, server_default="pcs"),
        )
        op.alter_column("items", "uom", server_default=None)

    bind = op.get_bind()
    inspector = inspect(bind)
    uq_names = {uc["name"] for uc in inspector.get_unique_constraints("items")}
    if "uq_items_tenant_barcode" not in uq_names:
        op.create_unique_constraint("uq_items_tenant_barcode", "items", ["tenant_id", "barcode"])

    ix_names = {ix["name"] for ix in inspector.get_indexes("items")}
    if "ix_items_barcode" not in ix_names:
        op.create_index("ix_items_barcode", "items", ["barcode"])


def downgrade() -> None:
    if _has_column("items", "barcode"):
        bind = op.get_bind()
        inspector = inspect(bind)
        ix_names = {ix["name"] for ix in inspector.get_indexes("items")}
        if "ix_items_barcode" in ix_names:
            op.drop_index("ix_items_barcode", table_name="items")
        uq_names = {uc["name"] for uc in inspector.get_unique_constraints("items")}
        if "uq_items_tenant_barcode" in uq_names:
            op.drop_constraint("uq_items_tenant_barcode", "items", type_="unique")
        op.drop_column("items", "barcode")
    if _has_column("items", "uom"):
        op.drop_column("items", "uom")
