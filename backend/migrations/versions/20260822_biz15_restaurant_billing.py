"""Restaurant billing fields on bills (BIZ-15).

Revision ID: 20260822_biz15_restaurant_billing
Revises: 20260822_biz14_kots
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz15_restaurant_billing"
down_revision = "20260822_biz14_kots"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column("bills", "order_id"):
        op.add_column("bills", sa.Column("order_id", sa.String(36), nullable=True))
        op.create_foreign_key(
            "fk_bills_order_id",
            "bills",
            "orders",
            ["order_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_bills_order_id", "bills", ["order_id"])
    if not _has_column("bills", "service_charge"):
        op.add_column(
            "bills",
            sa.Column("service_charge", sa.Numeric(12, 2), nullable=False, server_default="0"),
        )
    if not _has_column("bills", "split_group_id"):
        op.add_column("bills", sa.Column("split_group_id", sa.String(36), nullable=True))
        op.create_index("ix_bills_split_group_id", "bills", ["split_group_id"])


def downgrade() -> None:
    if _has_column("bills", "split_group_id"):
        op.drop_index("ix_bills_split_group_id", table_name="bills")
        op.drop_column("bills", "split_group_id")
    if _has_column("bills", "service_charge"):
        op.drop_column("bills", "service_charge")
    if _has_column("bills", "order_id"):
        op.drop_index("ix_bills_order_id", table_name="bills")
        op.drop_constraint("fk_bills_order_id", "bills", type_="foreignkey")
        op.drop_column("bills", "order_id")
