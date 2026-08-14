"""Composite bills index for report date+status filters.

Revision ID: 20260814_bill_report_index
Revises: 20260814_category_parent_key
Create Date: 2026-08-14
"""

from alembic import op


revision = "20260814_bill_report_index"
down_revision = "20260814_category_parent_key"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_bills_tenant_status_created_at",
        "bills",
        ["tenant_id", "status", "created_at"],
    )


def downgrade():
    op.drop_index("ix_bills_tenant_status_created_at", table_name="bills")
