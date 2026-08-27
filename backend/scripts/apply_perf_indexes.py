"""Add composite indexes for bill list / delivery / stock / POS hot paths (idempotent).

Prefer Alembic revision `20260826_biz66_perf_indexes` on app DBs.
This script remains for ops catch-up on hosts that only run SQL helpers.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def _has_index(conn, table: str, name: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                  AND INDEX_NAME = :name
                """
            ),
            {"table": table, "name": name},
        ).scalar()
    )


def _has_table(conn, table: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                """
            ),
            {"table": table},
        ).scalar()
    )


def _ensure_index(conn, table: str, name: str, ddl_cols: str) -> None:
    if not _has_table(conn, table):
        print(f"SKIP {table} (table missing)")
        return
    if _has_index(conn, table, name):
        print(f"{name} already exists")
        return
    conn.execute(text(f"CREATE INDEX {name} ON {table} ({ddl_cols})"))
    print(f"Created {name}")


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if _has_table(conn, "bill_deliveries"):
            _ensure_index(
                conn,
                "bill_deliveries",
                "ix_bill_deliveries_tenant_method_bill_created",
                "tenant_id, delivery_method, bill_id, created_at",
            )
        else:
            print("SKIP bill_deliveries (table missing)")

        _ensure_index(
            conn,
            "stock_movements",
            "ix_stock_movements_tenant_item_created",
            "tenant_id, item_id, created_at",
        )
        _ensure_index(conn, "bills", "ix_bills_tenant_created_at", "tenant_id, created_at")
        _ensure_index(
            conn,
            "items",
            "ix_items_tenant_active_name",
            "tenant_id, is_active, name",
        )
        _ensure_index(
            conn,
            "warehouse_stocks",
            "ix_warehouse_stocks_tenant_item",
            "tenant_id, item_id",
        )
        _ensure_index(
            conn,
            "serial_units",
            "ix_serial_units_tenant_status_received",
            "tenant_id, status, received_at",
        )

        # Hotel / cafe F&B hot paths (kitchen board + table open-order lookup)
        _ensure_index(
            conn,
            "kots",
            "ix_kots_tenant_status_created",
            "tenant_id, status, created_at",
        )
        _ensure_index(
            conn,
            "orders",
            "ix_orders_tenant_status_dining_table",
            "tenant_id, status, dining_table_id",
        )
        _ensure_index(
            conn,
            "dining_tables",
            "ix_dining_tables_tenant_active_status",
            "tenant_id, is_active, status",
        )
        _ensure_index(
            conn,
            "kot_items",
            "ix_kot_items_tenant_order_item",
            "tenant_id, order_item_id",
        )

    print("Performance indexes applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
