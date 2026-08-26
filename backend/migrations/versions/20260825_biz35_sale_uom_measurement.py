"""BIZ-35: item sale_uom for measurement billing.

Revision ID: 20260825_biz35_sale_uom_measurement
Revises: 20260825_biz33_installation_orders
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz35_sale_uom_measurement"
down_revision = "20260825_biz33_installation_orders"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "sale_uom"):
        op.add_column("items", sa.Column("sale_uom", sa.String(16), nullable=True))


def downgrade() -> None:
    if _has_column("items", "sale_uom"):
        op.drop_column("items", "sale_uom")
