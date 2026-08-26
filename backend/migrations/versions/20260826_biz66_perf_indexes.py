"""BIZ-66: tenant-leading composite indexes for POS / warehouse / ledger hot paths.

Revision ID: 20260826_biz66_perf_indexes
Revises: 20260826_biz59_travel_agent_commission
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz66_perf_indexes"
down_revision = "20260826_biz59_travel_agent_commission"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_index(table: str, name: str) -> bool:
    indexes = inspect(op.get_bind()).get_indexes(table)
    return any(idx.get("name") == name for idx in indexes)


def _create_index(name: str, table: str, columns: list[str]) -> None:
    if not _has_table(table):
        return
    if _has_index(table, name):
        return
    op.create_index(name, table, columns)


def upgrade() -> None:
    _create_index(
        "ix_items_tenant_active_name",
        "items",
        ["tenant_id", "is_active", "name"],
    )
    _create_index(
        "ix_warehouse_stocks_tenant_item",
        "warehouse_stocks",
        ["tenant_id", "item_id"],
    )
    _create_index(
        "ix_stock_movements_tenant_item_created",
        "stock_movements",
        ["tenant_id", "item_id", "created_at"],
    )
    _create_index(
        "ix_bills_tenant_created_at",
        "bills",
        ["tenant_id", "created_at"],
    )
    _create_index(
        "ix_serial_units_tenant_status_received",
        "serial_units",
        ["tenant_id", "status", "received_at"],
    )


def downgrade() -> None:
    for table, name in (
        ("serial_units", "ix_serial_units_tenant_status_received"),
        ("bills", "ix_bills_tenant_created_at"),
        ("stock_movements", "ix_stock_movements_tenant_item_created"),
        ("warehouse_stocks", "ix_warehouse_stocks_tenant_item"),
        ("items", "ix_items_tenant_active_name"),
    ):
        if _has_table(table) and _has_index(table, name):
            op.drop_index(name, table_name=table)
