"""BIZ-51: wholesale price lists, line prices, customer assignments.

Revision ID: 20260826_biz51_wholesale_price_lists
Revises: 20260826_biz49_furniture_delivery_tracking
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz51_wholesale_price_lists"
down_revision = "20260826_biz49_furniture_delivery_tracking"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("price_lists"):
        op.create_table(
            "price_lists",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("list_type", sa.String(20), nullable=False, server_default="WHOLESALE"),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "name", name="uq_price_lists_tenant_name"),
        )
        op.create_index("ix_price_lists_tenant_id", "price_lists", ["tenant_id"])

    if not _has_table("price_list_items"):
        op.create_table(
            "price_list_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "price_list_id",
                sa.String(36),
                sa.ForeignKey("price_lists.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "tenant_id",
                "price_list_id",
                "item_id",
                name="uq_price_list_items_tenant_list_item",
            ),
        )
        op.create_index("ix_price_list_items_tenant_id", "price_list_items", ["tenant_id"])
        op.create_index("ix_price_list_items_price_list_id", "price_list_items", ["price_list_id"])
        op.create_index("ix_price_list_items_item_id", "price_list_items", ["item_id"])

    if not _has_table("customer_price_lists"):
        op.create_table(
            "customer_price_lists",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "price_list_id",
                sa.String(36),
                sa.ForeignKey("price_lists.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("assigned_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "tenant_id",
                "customer_id",
                name="uq_customer_price_lists_tenant_customer",
            ),
        )
        op.create_index("ix_customer_price_lists_tenant_id", "customer_price_lists", ["tenant_id"])
        op.create_index("ix_customer_price_lists_customer_id", "customer_price_lists", ["customer_id"])
        op.create_index(
            "ix_customer_price_lists_price_list_id", "customer_price_lists", ["price_list_id"]
        )


def downgrade() -> None:
    if _has_table("customer_price_lists"):
        op.drop_index("ix_customer_price_lists_price_list_id", table_name="customer_price_lists")
        op.drop_index("ix_customer_price_lists_customer_id", table_name="customer_price_lists")
        op.drop_index("ix_customer_price_lists_tenant_id", table_name="customer_price_lists")
        op.drop_table("customer_price_lists")
    if _has_table("price_list_items"):
        op.drop_index("ix_price_list_items_item_id", table_name="price_list_items")
        op.drop_index("ix_price_list_items_price_list_id", table_name="price_list_items")
        op.drop_index("ix_price_list_items_tenant_id", table_name="price_list_items")
        op.drop_table("price_list_items")
    if _has_table("price_lists"):
        op.drop_index("ix_price_lists_tenant_id", table_name="price_lists")
        op.drop_table("price_lists")
