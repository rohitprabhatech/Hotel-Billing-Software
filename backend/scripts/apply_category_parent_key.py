"""Apply category root-name uniqueness via generated parent_key (MySQL).

MySQL UNIQUE (tenant_id, parent_id, name) allows multiple rows with the same
name when parent_id IS NULL. parent_key = IFNULL(parent_id, '') closes that gap.

Uses a VIRTUAL generated column (STORED ALTER can fail with errno 1215 when
rebuilding self-referential FK tables on existing DBs).

Idempotent. Requires DATABASE_URL.
"""

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
        dupes = conn.execute(
            text(
                """
                SELECT tenant_id, name, COUNT(*) AS cnt
                FROM categories
                WHERE parent_id IS NULL
                GROUP BY tenant_id, name
                HAVING COUNT(*) > 1
                """
            )
        ).fetchall()
        if dupes:
            print(
                "Duplicate main categories found — resolve before applying unique key:",
                file=sys.stderr,
            )
            for row in dupes:
                print(f"  tenant={row[0]} name={row[1]!r} count={row[2]}", file=sys.stderr)
            return 1

        if not _has_column(conn, "categories", "parent_key"):
            conn.execute(
                text(
                    """
                    ALTER TABLE categories
                    ADD COLUMN parent_key CHAR(36)
                    AS (IFNULL(parent_id, '')) VIRTUAL
                    AFTER parent_id
                    """
                )
            )
            print("Added categories.parent_key VIRTUAL generated column")
        else:
            print("categories.parent_key already exists")

        if _has_index(conn, "categories", "uq_categories_tenant_parent_name"):
            conn.execute(text("ALTER TABLE categories DROP INDEX uq_categories_tenant_parent_name"))
            print("Dropped uq_categories_tenant_parent_name")
        else:
            print("uq_categories_tenant_parent_name already absent")

        if not _has_index(conn, "categories", "uq_categories_tenant_parent_key_name"):
            conn.execute(
                text(
                    """
                    ALTER TABLE categories
                    ADD UNIQUE KEY uq_categories_tenant_parent_key_name
                    (tenant_id, parent_key, name)
                    """
                )
            )
            print("Created uq_categories_tenant_parent_key_name")
        else:
            print("uq_categories_tenant_parent_key_name already exists")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
