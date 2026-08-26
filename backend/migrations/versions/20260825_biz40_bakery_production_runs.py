"""BIZ-40: production_runs, production_run_items, counters.

Revision ID: 20260825_biz40_bakery_production_runs
Revises: 20260825_biz38_warehouse_stock_foundation
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz40_bakery_production_runs"
down_revision = "20260825_biz38_warehouse_stock_foundation"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("production_run_number_counters"):
        op.create_table(
            "production_run_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
        )

    if not _has_table("production_runs"):
        op.create_table(
            "production_runs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("run_number", sa.String(30), nullable=False),
            sa.Column(
                "recipe_id",
                sa.String(36),
                sa.ForeignKey("recipes.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "finished_item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("finished_item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("run_date", sa.Date(), nullable=False),
            sa.Column(
                "finished_stock_movement_id",
                sa.String(36),
                sa.ForeignKey("stock_movements.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "run_number", name="uq_production_runs_tenant_number"),
        )
        op.create_index("ix_production_runs_tenant_id", "production_runs", ["tenant_id"])
        op.create_index("ix_production_runs_recipe_id", "production_runs", ["recipe_id"])
        op.create_index(
            "ix_production_runs_finished_item_id", "production_runs", ["finished_item_id"]
        )
        op.create_index("ix_production_runs_run_date", "production_runs", ["run_date"])
        op.create_index(
            "ix_production_runs_finished_stock_movement_id",
            "production_runs",
            ["finished_stock_movement_id"],
        )

    if not _has_table("production_run_items"):
        op.create_table(
            "production_run_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "production_run_id",
                sa.String(36),
                sa.ForeignKey("production_runs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
            sa.Column("uom", sa.String(16), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "stock_movement_id",
                sa.String(36),
                sa.ForeignKey("stock_movements.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_production_run_items_tenant_id", "production_run_items", ["tenant_id"])
        op.create_index(
            "ix_production_run_items_production_run_id",
            "production_run_items",
            ["production_run_id"],
        )
        op.create_index("ix_production_run_items_item_id", "production_run_items", ["item_id"])
        op.create_index(
            "ix_production_run_items_stock_movement_id",
            "production_run_items",
            ["stock_movement_id"],
        )


def downgrade() -> None:
    if _has_table("production_run_items"):
        op.drop_table("production_run_items")
    if _has_table("production_runs"):
        op.drop_table("production_runs")
    if _has_table("production_run_number_counters"):
        op.drop_table("production_run_number_counters")
