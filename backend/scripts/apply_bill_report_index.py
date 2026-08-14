"""Add composite index for report/dashboard bill filters (MySQL).

Reports filter by tenant + status + created_at together. Existing separate
indexes help; this composite matches the hot path more directly.

Idempotent. Requires DATABASE_URL.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


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
        if not _has_index(conn, "bills", "ix_bills_tenant_status_created_at"):
            conn.execute(
                text(
                    """
                    CREATE INDEX ix_bills_tenant_status_created_at
                    ON bills (tenant_id, status, created_at)
                    """
                )
            )
            print("Created ix_bills_tenant_status_created_at")
        else:
            print("ix_bills_tenant_status_created_at already exists")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
