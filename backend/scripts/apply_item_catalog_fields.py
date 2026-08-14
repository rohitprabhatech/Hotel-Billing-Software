"""Apply items.sku / cost_price / stock_quantity without full Alembic."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def _has_column(conn, table: str, column: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                  AND COLUMN_NAME = :column
                """
            ),
            {"table": table, "column": column},
        ).scalar()
    )


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_column(conn, "items", "sku"):
            conn.execute(text("ALTER TABLE items ADD COLUMN sku VARCHAR(64) NULL AFTER name"))
            print("Added items.sku")
        else:
            print("items.sku already exists")

        if not _has_column(conn, "items", "cost_price"):
            conn.execute(
                text("ALTER TABLE items ADD COLUMN cost_price DECIMAL(12,2) NULL AFTER price")
            )
            print("Added items.cost_price")
        else:
            print("items.cost_price already exists")

        if not _has_column(conn, "items", "stock_quantity"):
            conn.execute(
                text(
                    "ALTER TABLE items ADD COLUMN stock_quantity DECIMAL(12,3) NULL "
                    "AFTER gst_percentage"
                )
            )
            print("Added items.stock_quantity")
        else:
            print("items.stock_quantity already exists")

        # Unique + index (ignore if already present)
        try:
            conn.execute(text("CREATE UNIQUE INDEX uq_items_tenant_sku ON items (tenant_id, sku)"))
            print("Created uq_items_tenant_sku")
        except Exception as exc:  # noqa: BLE001
            print(f"uq_items_tenant_sku skipped: {exc}")

        try:
            conn.execute(text("CREATE INDEX ix_items_tenant_sku ON items (tenant_id, sku)"))
            print("Created ix_items_tenant_sku")
        except Exception as exc:  # noqa: BLE001
            print(f"ix_items_tenant_sku skipped: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
