"""BIZ-56: tour packages for travel agencies.

Revision ID: 20260826_biz56_tour_packages
Revises: 20260826_biz52_sales_purchase_orders
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz56_tour_packages"
down_revision = "20260826_biz52_sales_purchase_orders"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("tour_packages"):
        op.create_table(
            "tour_packages",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("code", sa.String(40), nullable=False),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("destination", sa.String(160), nullable=True),
            sa.Column("duration_days", sa.Integer(), nullable=True),
            sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("gst_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "code", name="uq_tour_packages_tenant_code"),
            sa.UniqueConstraint("tenant_id", "item_id", name="uq_tour_packages_tenant_item"),
        )
        op.create_index("ix_tour_packages_tenant_id", "tour_packages", ["tenant_id"])
        op.create_index("ix_tour_packages_item_id", "tour_packages", ["item_id"])


def downgrade() -> None:
    if _has_table("tour_packages"):
        op.drop_table("tour_packages")
