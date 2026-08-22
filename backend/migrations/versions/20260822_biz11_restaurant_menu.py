"""Add restaurant menu item attributes (BIZ-11).

Revision ID: 20260822_biz11_restaurant_menu
Revises: 20260822_biz09_party_ledger
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz11_restaurant_menu"
down_revision = "20260822_biz09_party_ledger"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    return column in {col["name"] for col in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("items", "is_menu"):
        op.add_column(
            "items",
            sa.Column("is_menu", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        op.alter_column("items", "is_menu", server_default=None)
    if not _has_column("items", "is_veg"):
        op.add_column("items", sa.Column("is_veg", sa.Boolean(), nullable=True))


def downgrade() -> None:
    if _has_column("items", "is_veg"):
        op.drop_column("items", "is_veg")
    if _has_column("items", "is_menu"):
        op.drop_column("items", "is_menu")
