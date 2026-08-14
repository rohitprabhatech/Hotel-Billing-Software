"""Add tenants.business_type for multi-business SaaS.

Revision ID: 20260814_tenant_business_type
Revises: 20260326_bill_payment_method
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_tenant_business_type"
down_revision = "20260326_bill_payment_method"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tenants") as batch:
        batch.add_column(
            sa.Column(
                "business_type",
                sa.String(length=40),
                nullable=False,
                server_default="other",
            )
        )
        batch.create_index("ix_tenants_business_type", ["business_type"])


def downgrade():
    with op.batch_alter_table("tenants") as batch:
        batch.drop_index("ix_tenants_business_type")
        batch.drop_column("business_type")
