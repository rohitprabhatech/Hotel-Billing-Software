"""Cafe add-ons, combos, and order line extensions (BIZ-17).

Revision ID: 20260822_biz17_cafe_addons_combos
Revises: 20260822_biz16_recipes
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz17_cafe_addons_combos"
down_revision = "20260822_biz16_recipes"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("item_addon_groups"):
        op.create_table(
            "item_addon_groups",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("menu_item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("max_selections", sa.Integer(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_item_addon_groups_tenant_id", "item_addon_groups", ["tenant_id"])
        op.create_index("ix_item_addon_groups_menu_item_id", "item_addon_groups", ["menu_item_id"])

    if not _has_table("item_addons"):
        op.create_table(
            "item_addons",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("group_id", sa.String(36), sa.ForeignKey("item_addon_groups.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("extra_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("linked_item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="SET NULL"), nullable=True),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_item_addons_tenant_id", "item_addons", ["tenant_id"])
        op.create_index("ix_item_addons_group_id", "item_addons", ["group_id"])
        op.create_index("ix_item_addons_linked_item_id", "item_addons", ["linked_item_id"])

    if not _has_table("combos"):
        op.create_table(
            "combos",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("combo_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("is_popular", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "name", name="uq_combos_tenant_name"),
        )
        op.create_index("ix_combos_tenant_id", "combos", ["tenant_id"])

    if not _has_table("combo_items"):
        op.create_table(
            "combo_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("combo_id", sa.String(36), sa.ForeignKey("combos.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False, server_default="1"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_combo_items_tenant_id", "combo_items", ["tenant_id"])
        op.create_index("ix_combo_items_combo_id", "combo_items", ["combo_id"])
        op.create_index("ix_combo_items_item_id", "combo_items", ["item_id"])

    bind = op.get_bind()
    order_items_cols = {col["name"] for col in inspect(bind).get_columns("order_items")}
    if "combo_id" not in order_items_cols:
        op.add_column(
            "order_items",
            sa.Column("combo_id", sa.String(36), sa.ForeignKey("combos.id", ondelete="SET NULL"), nullable=True),
        )
        op.create_index("ix_order_items_combo_id", "order_items", ["combo_id"])

    if not _has_table("order_item_addons"):
        op.create_table(
            "order_item_addons",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("order_item_id", sa.String(36), sa.ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False),
            sa.Column("addon_id", sa.String(36), sa.ForeignKey("item_addons.id", ondelete="SET NULL"), nullable=True),
            sa.Column("addon_name", sa.String(120), nullable=False),
            sa.Column("extra_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_order_item_addons_tenant_id", "order_item_addons", ["tenant_id"])
        op.create_index("ix_order_item_addons_order_item_id", "order_item_addons", ["order_item_id"])
        op.create_index("ix_order_item_addons_addon_id", "order_item_addons", ["addon_id"])


def downgrade() -> None:
    if _has_table("order_item_addons"):
        op.drop_index("ix_order_item_addons_addon_id", table_name="order_item_addons")
        op.drop_index("ix_order_item_addons_order_item_id", table_name="order_item_addons")
        op.drop_index("ix_order_item_addons_tenant_id", table_name="order_item_addons")
        op.drop_table("order_item_addons")

    bind = op.get_bind()
    order_items_cols = {col["name"] for col in inspect(bind).get_columns("order_items")} if _has_table("order_items") else set()
    if "combo_id" in order_items_cols:
        op.drop_index("ix_order_items_combo_id", table_name="order_items")
        op.drop_column("order_items", "combo_id")

    if _has_table("combo_items"):
        op.drop_index("ix_combo_items_item_id", table_name="combo_items")
        op.drop_index("ix_combo_items_combo_id", table_name="combo_items")
        op.drop_index("ix_combo_items_tenant_id", table_name="combo_items")
        op.drop_table("combo_items")
    if _has_table("combos"):
        op.drop_index("ix_combos_tenant_id", table_name="combos")
        op.drop_table("combos")
    if _has_table("item_addons"):
        op.drop_index("ix_item_addons_linked_item_id", table_name="item_addons")
        op.drop_index("ix_item_addons_group_id", table_name="item_addons")
        op.drop_index("ix_item_addons_tenant_id", table_name="item_addons")
        op.drop_table("item_addons")
    if _has_table("item_addon_groups"):
        op.drop_index("ix_item_addon_groups_menu_item_id", table_name="item_addon_groups")
        op.drop_index("ix_item_addon_groups_tenant_id", table_name="item_addon_groups")
        op.drop_table("item_addon_groups")
