"""Purchases + purchase_items tables (BIZ-06).

Revision ID: 20260822_biz06_purchases
Revises: 20260822_biz05_suppliers
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz06_purchases"
down_revision = "20260822_biz05_suppliers"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("purchase_number_counters"):
        op.create_table(
            "purchase_number_counters",
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), primary_key=True),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    if not _has_table("purchases"):
        op.create_table(
            "purchases",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
            sa.Column("purchase_number", sa.String(50), nullable=False),
            sa.Column("purchase_sequence", sa.Integer(), nullable=False),
            sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=True),
            sa.Column("supplier_name", sa.String(120), nullable=True),
            sa.Column("invoice_number", sa.String(60), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(20), nullable=False, server_default="FINALIZED"),
            sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("cancelled_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("cancelled_at", sa.DateTime(), nullable=True),
            sa.Column("cancellation_reason", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "purchase_number", name="uq_purchases_tenant_number"),
            sa.UniqueConstraint("tenant_id", "purchase_sequence", name="uq_purchases_tenant_sequence"),
        )
        op.create_index("ix_purchases_tenant_id", "purchases", ["tenant_id"])
        op.create_index("ix_purchases_supplier_id", "purchases", ["supplier_id"])

    if not _has_table("purchase_items"):
        op.create_table(
            "purchase_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
            sa.Column("purchase_id", sa.String(36), sa.ForeignKey("purchases.id"), nullable=False),
            sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id"), nullable=False),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
            sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_purchase_items_tenant_id", "purchase_items", ["tenant_id"])
        op.create_index("ix_purchase_items_purchase_id", "purchase_items", ["purchase_id"])
        op.create_index("ix_purchase_items_item_id", "purchase_items", ["item_id"])


def downgrade() -> None:
    if _has_table("purchase_items"):
        op.drop_index("ix_purchase_items_item_id", table_name="purchase_items")
        op.drop_index("ix_purchase_items_purchase_id", table_name="purchase_items")
        op.drop_index("ix_purchase_items_tenant_id", table_name="purchase_items")
        op.drop_table("purchase_items")
    if _has_table("purchases"):
        op.drop_index("ix_purchases_supplier_id", table_name="purchases")
        op.drop_index("ix_purchases_tenant_id", table_name="purchases")
        op.drop_table("purchases")
    if _has_table("purchase_number_counters"):
        op.drop_table("purchase_number_counters")
