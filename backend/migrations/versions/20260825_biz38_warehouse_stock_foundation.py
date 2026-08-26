"""BIZ-38: warehouses, warehouse_stocks, stock transfers.

Revision ID: 20260825_biz38_warehouse_stock_foundation
Revises: 20260825_biz37_transport_supplier_credit
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz38_warehouse_stock_foundation"
down_revision = "20260825_biz37_transport_supplier_credit"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_table("warehouses"):
        op.create_table(
            "warehouses",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("code", sa.String(30), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "code", name="uq_warehouses_tenant_code"),
        )
        op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"])

    if not _has_table("warehouse_stocks"):
        op.create_table(
            "warehouse_stocks",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "warehouse_id",
                sa.String(36),
                sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("quantity", sa.Numeric(12, 3), nullable=False, server_default="0"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id",
                "warehouse_id",
                "item_id",
                name="uq_warehouse_stocks_tenant_wh_item",
            ),
        )
        op.create_index("ix_warehouse_stocks_tenant_id", "warehouse_stocks", ["tenant_id"])
        op.create_index("ix_warehouse_stocks_warehouse_id", "warehouse_stocks", ["warehouse_id"])
        op.create_index("ix_warehouse_stocks_item_id", "warehouse_stocks", ["item_id"])

    if not _has_table("stock_transfer_number_counters"):
        op.create_table(
            "stock_transfer_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("stock_transfers"):
        op.create_table(
            "stock_transfers",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("transfer_number", sa.String(50), nullable=False),
            sa.Column("transfer_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "from_warehouse_id",
                sa.String(36),
                sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "to_warehouse_id",
                sa.String(36),
                sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("status", sa.String(20), nullable=False, server_default="COMPLETED"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id", "transfer_number", name="uq_stock_transfers_tenant_number"
            ),
        )
        op.create_index("ix_stock_transfers_tenant_id", "stock_transfers", ["tenant_id"])
        op.create_index(
            "ix_stock_transfers_from_warehouse_id", "stock_transfers", ["from_warehouse_id"]
        )
        op.create_index(
            "ix_stock_transfers_to_warehouse_id", "stock_transfers", ["to_warehouse_id"]
        )

    if not _has_table("stock_transfer_items"):
        op.create_table(
            "stock_transfer_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "transfer_id",
                sa.String(36),
                sa.ForeignKey("stock_transfers.id", ondelete="CASCADE"),
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
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_stock_transfer_items_tenant_id", "stock_transfer_items", ["tenant_id"])
        op.create_index(
            "ix_stock_transfer_items_transfer_id", "stock_transfer_items", ["transfer_id"]
        )

    if not _has_column("bills", "warehouse_id"):
        op.add_column(
            "bills",
            sa.Column(
                "warehouse_id",
                sa.String(36),
                sa.ForeignKey("warehouses.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("ix_bills_warehouse_id", "bills", ["warehouse_id"])


def downgrade() -> None:
    if _has_column("bills", "warehouse_id"):
        try:
            op.drop_index("ix_bills_warehouse_id", table_name="bills")
        except Exception:
            pass
        op.drop_column("bills", "warehouse_id")
    for table, indexes in (
        ("stock_transfer_items", ("ix_stock_transfer_items_transfer_id", "ix_stock_transfer_items_tenant_id")),
        ("stock_transfers", ("ix_stock_transfers_to_warehouse_id", "ix_stock_transfers_from_warehouse_id", "ix_stock_transfers_tenant_id")),
        ("warehouse_stocks", ("ix_warehouse_stocks_item_id", "ix_warehouse_stocks_warehouse_id", "ix_warehouse_stocks_tenant_id")),
        ("warehouses", ("ix_warehouses_tenant_id",)),
    ):
        if _has_table(table):
            for index in indexes:
                try:
                    op.drop_index(index, table_name=table)
                except Exception:
                    pass
            op.drop_table(table)
    if _has_table("stock_transfer_number_counters"):
        op.drop_table("stock_transfer_number_counters")
