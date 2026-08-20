"""Widen WhatsApp delivery statuses + provider message index (idempotent)."""

from __future__ import annotations

import os
import sys

from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sqlalchemy import create_engine, text

from schema_helpers import check_clause, drop_check_constraint


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


def _has_index(conn, table: str, index_name: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                  AND INDEX_NAME = :index_name
                """
            ),
            {"table": table, "index_name": index_name},
        ).scalar()
    )


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_column(conn, "bill_deliveries", "delivered_at"):
            conn.execute(text("ALTER TABLE bill_deliveries ADD COLUMN delivered_at DATETIME(6) NULL AFTER sent_at"))
            print("Added bill_deliveries.delivered_at")
        else:
            print("bill_deliveries.delivered_at already exists")

        if not _has_column(conn, "bill_deliveries", "read_at"):
            conn.execute(text("ALTER TABLE bill_deliveries ADD COLUMN read_at DATETIME(6) NULL AFTER delivered_at"))
            print("Added bill_deliveries.read_at")
        else:
            print("bill_deliveries.read_at already exists")

        clause = check_clause(conn, "chk_bill_deliveries_status") or ""
        wanted = ("PENDING", "SENT", "DELIVERED", "READ", "FAILED")
        if all(token in clause.upper() for token in wanted):
            print("chk_bill_deliveries_status already includes DELIVERED/READ")
        else:
            drop_check_constraint(conn, "bill_deliveries", "chk_bill_deliveries_status")
            try:
                conn.execute(
                    text(
                        """
                        ALTER TABLE bill_deliveries
                        ADD CONSTRAINT chk_bill_deliveries_status
                        CHECK (status IN ('PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED'))
                        """
                    )
                )
                print("Updated chk_bill_deliveries_status")
            except Exception as exc:
                print(f"CHECK constraint note: {exc}")

        if not _has_index(conn, "bill_deliveries", "ix_bill_deliveries_provider_message"):
            conn.execute(
                text(
                    "CREATE INDEX ix_bill_deliveries_provider_message ON bill_deliveries (provider_message_id)"
                )
            )
            print("Added ix_bill_deliveries_provider_message")
        else:
            print("ix_bill_deliveries_provider_message already exists")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
