"""BIZ-37: transport charges + supplier ledger balances.

Revision ID: 20260825_biz37_transport_supplier_credit
Revises: 20260825_biz36_quotations_delivery_challans
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz37_transport_supplier_credit"
down_revision = "20260825_biz36_quotations_delivery_challans"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("bills", "transport_charge"):
        op.add_column(
            "bills",
            sa.Column(
                "transport_charge",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
        )
    if not _has_column("delivery_challans", "transport_charge"):
        op.add_column(
            "delivery_challans",
            sa.Column(
                "transport_charge",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
        )
    if not _has_column("suppliers", "balance"):
        op.add_column(
            "suppliers",
            sa.Column(
                "balance",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
        )
    if not _has_column("suppliers", "credit_limit"):
        op.add_column(
            "suppliers",
            sa.Column("credit_limit", sa.Numeric(12, 2), nullable=True),
        )


def downgrade() -> None:
    if _has_column("suppliers", "credit_limit"):
        op.drop_column("suppliers", "credit_limit")
    if _has_column("suppliers", "balance"):
        op.drop_column("suppliers", "balance")
    if _has_column("delivery_challans", "transport_charge"):
        op.drop_column("delivery_challans", "transport_charge")
    if _has_column("bills", "transport_charge"):
        op.drop_column("bills", "transport_charge")
