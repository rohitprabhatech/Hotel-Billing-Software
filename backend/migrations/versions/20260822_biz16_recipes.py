"""Add recipes and recipe_ingredients (BIZ-16).

Revision ID: 20260822_biz16_recipes
Revises: 20260822_biz15_restaurant_billing
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz16_recipes"
down_revision = "20260822_biz15_restaurant_billing"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("recipes"):
        return

    op.create_table(
        "recipes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("menu_item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("yield_quantity", sa.Numeric(10, 3), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "menu_item_id", name="uq_recipes_tenant_menu_item"),
    )
    op.create_index("ix_recipes_tenant_id", "recipes", ["tenant_id"])
    op.create_index("ix_recipes_menu_item_id", "recipes", ["menu_item_id"])

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("recipe_id", sa.String(36), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_item_id", sa.String(36), sa.ForeignKey("items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ingredient_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("uom", sa.String(16), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "recipe_id", "ingredient_item_id", name="uq_recipe_ingredients_item"),
    )
    op.create_index("ix_recipe_ingredients_tenant_id", "recipe_ingredients", ["tenant_id"])
    op.create_index("ix_recipe_ingredients_recipe_id", "recipe_ingredients", ["recipe_id"])


def downgrade() -> None:
    if _has_table("recipe_ingredients"):
        op.drop_index("ix_recipe_ingredients_recipe_id", table_name="recipe_ingredients")
        op.drop_index("ix_recipe_ingredients_tenant_id", table_name="recipe_ingredients")
        op.drop_table("recipe_ingredients")
    if _has_table("recipes"):
        op.drop_index("ix_recipes_menu_item_id", table_name="recipes")
        op.drop_index("ix_recipes_tenant_id", table_name="recipes")
        op.drop_table("recipes")
