"""Suppliers table (BIZ-05).

Revision ID: 20260822_biz05_suppliers
Revises: 20260822_biz04_customers
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz05_suppliers"
down_revision = "20260822_biz04_customers"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("suppliers"):
        return
    op.create_table(
        "suppliers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("phone_country_code", sa.String(8), nullable=True),
        sa.Column("phone_national", sa.String(20), nullable=True),
        sa.Column("phone_e164", sa.String(20), nullable=True),
        sa.Column("gstin", sa.String(15), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("tenant_id", "phone_e164", name="uq_suppliers_tenant_phone_e164"),
        sa.UniqueConstraint("tenant_id", "gstin", name="uq_suppliers_tenant_gstin"),
    )
    op.create_index("ix_suppliers_tenant_id", "suppliers", ["tenant_id"])


def downgrade() -> None:
    if not _has_table("suppliers"):
        return
    op.drop_index("ix_suppliers_tenant_id", table_name="suppliers")
    op.drop_table("suppliers")
