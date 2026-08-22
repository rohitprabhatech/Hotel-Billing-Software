"""Add dining_tables (BIZ-12).

Revision ID: 20260822_biz12_dining_tables
Revises: 20260822_biz11_restaurant_menu
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz12_dining_tables"
down_revision = "20260822_biz11_restaurant_menu"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("dining_tables"):
        return
    op.create_table(
        "dining_tables",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("section", sa.String(64), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="available"),
        sa.Column("merged_into_id", sa.String(36), sa.ForeignKey("dining_tables.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_dining_tables_tenant_code"),
    )
    op.create_index("ix_dining_tables_tenant_id", "dining_tables", ["tenant_id"])
    op.create_index("ix_dining_tables_merged_into_id", "dining_tables", ["merged_into_id"])


def downgrade() -> None:
    if not _has_table("dining_tables"):
        return
    op.drop_index("ix_dining_tables_merged_into_id", table_name="dining_tables")
    op.drop_index("ix_dining_tables_tenant_id", table_name="dining_tables")
    op.drop_table("dining_tables")
