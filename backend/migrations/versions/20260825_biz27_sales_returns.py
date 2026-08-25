"""Sales returns and exchanges (BIZ-27).

Revision ID: 20260825_biz27_sales_returns
Revises: 20260825_biz26_item_images
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz27_sales_returns"
down_revision = "20260825_biz26_item_images"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("sales_return_counters"):
        op.create_table(
            "sales_return_counters",
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("sales_returns"):
        op.create_table(
            "sales_returns",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("bill_id", sa.String(36), sa.ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("return_number", sa.String(50), nullable=False),
            sa.Column("return_sequence", sa.Integer(), nullable=False),
            sa.Column("kind", sa.String(16), nullable=False, server_default="RETURN"),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("refund_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("extra_payable", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(20), nullable=False, server_default="FINALIZED"),
            sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "return_number", name="uq_sales_returns_tenant_number"),
        )
        op.create_index("ix_sales_returns_tenant_id", "sales_returns", ["tenant_id"])
        op.create_index("ix_sales_returns_bill_id", "sales_returns", ["bill_id"])

    if not _has_table("sales_return_items"):
        op.create_table(
            "sales_return_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("return_id", sa.String(36), sa.ForeignKey("sales_returns.id", ondelete="CASCADE"), nullable=False),
            sa.Column("bill_item_id", sa.String(36), sa.ForeignKey("bill_items.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="SET NULL"), nullable=True),
            sa.Column("variant_id", sa.String(36), sa.ForeignKey("item_variants.id", ondelete="SET NULL"), nullable=True),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("line_refund", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("exchange_item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="SET NULL"), nullable=True),
            sa.Column("exchange_variant_id", sa.String(36), sa.ForeignKey("item_variants.id", ondelete="SET NULL"), nullable=True),
            sa.Column("exchange_item_name", sa.String(200), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_sales_return_items_tenant_id", "sales_return_items", ["tenant_id"])
        op.create_index("ix_sales_return_items_return_id", "sales_return_items", ["return_id"])


def downgrade() -> None:
    if _has_table("sales_return_items"):
        op.drop_index("ix_sales_return_items_return_id", table_name="sales_return_items")
        op.drop_index("ix_sales_return_items_tenant_id", table_name="sales_return_items")
        op.drop_table("sales_return_items")
    if _has_table("sales_returns"):
        op.drop_index("ix_sales_returns_bill_id", table_name="sales_returns")
        op.drop_index("ix_sales_returns_tenant_id", table_name="sales_returns")
        op.drop_table("sales_returns")
    if _has_table("sales_return_counters"):
        op.drop_table("sales_return_counters")
