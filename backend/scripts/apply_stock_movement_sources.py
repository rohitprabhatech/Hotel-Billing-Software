"""Widen stock_movements.source CHECK to all app-used sources (idempotent).

Fixes hotel/table bill settle failing with:
  CONSTRAINT `chk_stock_movements_source` failed
when recording RECIPE (and other) stock movements.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_BACKEND = _SCRIPTS.parent
for path in (_BACKEND, _SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sqlalchemy import create_engine, text

from schema_helpers import check_clause, drop_check_constraint

ALLOWED_SOURCES = (
    "BILL",
    "CANCEL",
    "ADJUST",
    "ITEM_UPDATE",
    "RECEIVE",
    "PURCHASE",
    "PURCHASE_CANCEL",
    "RECIPE",
    "WASTAGE",
    "RETURN",
    "EXCHANGE",
    "TRANSFER_OUT",
    "TRANSFER_IN",
    "PRODUCTION",
)

_SOURCE_LIST = ", ".join(f"'{s}'" for s in ALLOWED_SOURCES)
_CHECK_SQL = f"CHECK (source IN ({_SOURCE_LIST}))"


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


def _already_current(clause: str | None) -> bool:
    if not clause:
        return False
    upper = clause.upper()
    return all(source in upper for source in ALLOWED_SOURCES)


def main() -> int:
    from app.utils.database_url import load_backend_env, resolve_database_url

    load_backend_env()
    url = os.environ.get("DATABASE_URL") or resolve_database_url()
    if not url:
        print("DATABASE_URL or MYSQL_* is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_table(conn, "stock_movements"):
            print("stock_movements table missing — run apply_stock_movements.py first")
            return 1

        clause = check_clause(conn, "chk_stock_movements_source")
        if _already_current(clause):
            print("stock_movements source CHECK already includes RECIPE and related sources")
            return 0

        drop_check_constraint(conn, "stock_movements", "chk_stock_movements_source")
        conn.execute(
            text(
                f"""
                ALTER TABLE stock_movements
                ADD CONSTRAINT chk_stock_movements_source
                {_CHECK_SQL}
                """
            )
        )
        print("stock_movements source CHECK widened (includes RECIPE, PURCHASE, WASTAGE, …)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
