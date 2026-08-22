"""Customers table + bills.customer_id (BIZ-04).

Revision ID: 20260822_biz04_customers
Revises: 20260822_biz03_manager_role
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz04_customers"
down_revision = "20260822_biz03_manager_role"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _column_exists(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_table("customers"):
        op.create_table(
            "customers",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("phone_country_code", sa.String(8), nullable=True),
            sa.Column("phone_national", sa.String(20), nullable=True),
            sa.Column("phone_e164", sa.String(20), nullable=True),
            sa.Column("email", sa.String(255), nullable=True),
            sa.Column("credit_limit", sa.Numeric(12, 2), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "phone_e164", name="uq_customers_tenant_phone_e164"),
        )
        op.create_index("ix_customers_tenant_id", "customers", ["tenant_id"])

    if _has_table("bills") and not _column_exists("bills", "customer_id"):
        op.add_column(
            "bills",
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("ix_bills_customer_id", "bills", ["customer_id"])


def downgrade() -> None:
    if _has_table("bills") and _column_exists("bills", "customer_id"):
        op.drop_index("ix_bills_customer_id", table_name="bills")
        op.drop_column("bills", "customer_id")
    if _has_table("customers"):
        op.drop_index("ix_customers_tenant_id", table_name="customers")
        op.drop_table("customers")
