"""Add transport_type to tour packages.

Revision ID: 20260902_tour_package_transport_type
Revises: 20260831_bills_payment_method_credit_check
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260902_tour_package_transport_type"
down_revision = "20260831_bills_payment_method_credit_check"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_column("tour_packages", "transport_type"):
        op.add_column(
            "tour_packages",
            sa.Column("transport_type", sa.String(60), nullable=True),
        )


def downgrade() -> None:
    if _has_column("tour_packages", "transport_type"):
        op.drop_column("tour_packages", "transport_type")
