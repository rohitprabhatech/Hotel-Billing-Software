"""Hotel billing: tenant print settings + audit soft-delete flag.

Revision ID: 20260827_hotel_billing_settings_audit_delete
Revises: 20260826_biz66_perf_indexes
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260827_hotel_billing_settings_audit_delete"
down_revision = "20260826_biz66_perf_indexes"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_column("audit_logs", "is_deleted"):
        op.add_column(
            "audit_logs",
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if not _has_column("tenants", "bill_paper_size"):
        op.add_column("tenants", sa.Column("bill_paper_size", sa.String(length=20), nullable=True))
    if not _has_column("tenants", "bill_width_mm"):
        op.add_column("tenants", sa.Column("bill_width_mm", sa.Integer(), nullable=True))
    if not _has_column("tenants", "bill_height_mm"):
        op.add_column("tenants", sa.Column("bill_height_mm", sa.Integer(), nullable=True))


def downgrade() -> None:
    if _has_column("tenants", "bill_height_mm"):
        op.drop_column("tenants", "bill_height_mm")
    if _has_column("tenants", "bill_width_mm"):
        op.drop_column("tenants", "bill_width_mm")
    if _has_column("tenants", "bill_paper_size"):
        op.drop_column("tenants", "bill_paper_size")
    if _has_column("audit_logs", "is_deleted"):
        op.drop_column("audit_logs", "is_deleted")
