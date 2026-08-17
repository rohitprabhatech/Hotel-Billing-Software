"""Add items.created_by for item activity attribution.

Revision ID: 20260326_item_created_by
Revises: 20260326_saas_auth
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260326_item_created_by"
down_revision = "20260326_saas_auth"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("items") as batch:
        batch.add_column(sa.Column("created_by", sa.String(length=36), nullable=True))
        batch.create_foreign_key(
            "fk_items_created_by_users",
            "users",
            ["created_by"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_items_created_by", ["created_by"])


def downgrade():
    with op.batch_alter_table("items") as batch:
        batch.drop_index("ix_items_created_by")
        batch.drop_constraint("fk_items_created_by_users", type_="foreignkey")
        batch.drop_column("created_by")
