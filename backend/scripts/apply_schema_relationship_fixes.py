"""Apply Sprint 4 relationship fixes without full Alembic (dev/ops helper).

Idempotent for MySQL.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def _fk_on_delete(conn, table: str, constraint: str) -> str | None:
    row = conn.execute(
        text(
            """
            SELECT DELETE_RULE
            FROM information_schema.REFERENTIAL_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
              AND TABLE_NAME = :table
              AND CONSTRAINT_NAME = :constraint
            """
        ),
        {"table": table, "constraint": constraint},
    ).fetchone()
    return row[0] if row else None


def _column_default(conn, table: str, column: str) -> str | None:
    row = conn.execute(
        text(
            """
            SELECT COLUMN_DEFAULT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table
              AND COLUMN_NAME = :column
            """
        ),
        {"table": table, "column": column},
    ).fetchone()
    return row[0] if row else None


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        default = _column_default(conn, "bills", "status")
        normalized = (default or "").strip().strip("'").strip('"')
        if normalized != "FINALIZED":
            conn.execute(
                text(
                    "ALTER TABLE bills MODIFY status VARCHAR(20) NOT NULL DEFAULT 'FINALIZED'"
                )
            )
            print("Updated bills.status default -> FINALIZED")
        else:
            print("bills.status default already FINALIZED")

        rule = _fk_on_delete(conn, "bill_items", "fk_bill_items_item")
        if rule != "SET NULL":
            conn.execute(text("ALTER TABLE bill_items DROP FOREIGN KEY fk_bill_items_item"))
            conn.execute(
                text(
                    """
                    ALTER TABLE bill_items
                    ADD CONSTRAINT fk_bill_items_item
                    FOREIGN KEY (item_id) REFERENCES items (id)
                    ON DELETE SET NULL ON UPDATE CASCADE
                    """
                )
            )
            print("Updated fk_bill_items_item ON DELETE SET NULL")
        else:
            print("fk_bill_items_item already SET NULL")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
