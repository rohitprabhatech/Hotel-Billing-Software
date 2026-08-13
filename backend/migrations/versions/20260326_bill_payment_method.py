"""Add bills.payment_method for cash/online.

Revision ID: 20260326_bill_payment_method
Revises: 20260326_item_created_by
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260326_bill_payment_method"
down_revision = "20260326_item_created_by"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("bills") as batch:
        batch.add_column(
            sa.Column(
                "payment_method",
                sa.String(length=20),
                nullable=False,
                server_default="cash",
            )
        )
        batch.create_index(
            "ix_bills_tenant_payment_method",
            ["tenant_id", "payment_method"],
        )


def downgrade():
    with op.batch_alter_table("bills") as batch:
        batch.drop_index("ix_bills_tenant_payment_method")
        batch.drop_column("payment_method")
