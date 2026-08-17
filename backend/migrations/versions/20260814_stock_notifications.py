"""Add minimum_stock_level and notifications table.

Revision ID: 20260814_stock_notifications
Revises: 20260814_bill_report_index
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_stock_notifications"
down_revision = "20260814_bill_report_index"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("items") as batch:
        batch.add_column(
            sa.Column("minimum_stock_level", sa.Numeric(12, 3), nullable=True)
        )

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_notifications_tenant_created",
        "notifications",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_notifications_tenant_unread",
        "notifications",
        ["tenant_id", "is_read", "created_at"],
    )


def downgrade():
    op.drop_index("ix_notifications_tenant_unread", table_name="notifications")
    op.drop_index("ix_notifications_tenant_created", table_name="notifications")
    op.drop_table("notifications")
    with op.batch_alter_table("items") as batch:
        batch.drop_column("minimum_stock_level")
