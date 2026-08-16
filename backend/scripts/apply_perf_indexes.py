"""Add composite indexes for bill list / delivery / stock hot paths (idempotent)."""

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


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if _has_table(conn, "bill_deliveries"):
            name = "ix_bill_deliveries_tenant_method_bill_created"
            if not _has_index(conn, "bill_deliveries", name):
                conn.execute(
                    text(
                        f"""
                        CREATE INDEX {name}
                        ON bill_deliveries (tenant_id, delivery_method, bill_id, created_at)
                        """
                    )
                )
                print(f"Created {name}")
            else:
                print(f"{name} already exists")
        else:
            print("SKIP bill_deliveries (table missing)")

        if _has_table(conn, "stock_movements"):
            name = "ix_stock_movements_tenant_item_created"
            if not _has_index(conn, "stock_movements", name):
                conn.execute(
                    text(
                        f"""
                        CREATE INDEX {name}
                        ON stock_movements (tenant_id, item_id, created_at)
                        """
                    )
                )
                print(f"Created {name}")
            else:
                print(f"{name} already exists")
        else:
            print("SKIP stock_movements (table missing)")

        if _has_table(conn, "bills"):
            name = "ix_bills_tenant_created_at"
            if not _has_index(conn, "bills", name):
                conn.execute(
                    text(
                        f"CREATE INDEX {name} ON bills (tenant_id, created_at)"
                    )
                )
                print(f"Created {name}")
            else:
                print(f"{name} already exists")

    print("Performance indexes applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
