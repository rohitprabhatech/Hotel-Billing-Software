"""Add bill_format to tenants for printable bill layout.

Revision ID: 20260902_tenant_bill_format
Revises: 20260902_tour_package_transport_type
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260902_tenant_bill_format"
down_revision = "20260902_tour_package_transport_type"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_column("tenants", "bill_format"):
        op.add_column(
            "tenants",
            sa.Column("bill_format", sa.String(20), nullable=True),
        )


def downgrade() -> None:
    if _has_column("tenants", "bill_format"):
        op.drop_column("tenants", "bill_format")
