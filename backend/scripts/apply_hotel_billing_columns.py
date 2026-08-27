"""Apply hotel billing settings + audit soft-delete columns (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine, inspect, text

from app.utils.database_url import load_backend_env, resolve_database_url


def main() -> int:
    load_backend_env()
    url = resolve_database_url()
    if not url:
        print("DATABASE_URL / MYSQL_* required")
        return 1

    engine = create_engine(url)
    insp = inspect(engine)

    def has_col(table: str, col: str) -> bool:
        return col in {c["name"] for c in insp.get_columns(table)}

    stmts: list[str] = []
    if not has_col("audit_logs", "is_deleted"):
        stmts.append(
            "ALTER TABLE audit_logs ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0"
        )
    if not has_col("tenants", "bill_paper_size"):
        stmts.append("ALTER TABLE tenants ADD COLUMN bill_paper_size VARCHAR(20) NULL")
    if not has_col("tenants", "bill_width_mm"):
        stmts.append("ALTER TABLE tenants ADD COLUMN bill_width_mm INT NULL")
    if not has_col("tenants", "bill_height_mm"):
        stmts.append("ALTER TABLE tenants ADD COLUMN bill_height_mm INT NULL")

    with engine.begin() as conn:
        if not stmts:
            print("Hotel billing columns already present")
        for sql in stmts:
            conn.execute(text(sql))
            print(f"Applied: {sql}")

    insp = inspect(engine)
    checks = [
        ("audit_logs", "is_deleted"),
        ("tenants", "bill_paper_size"),
        ("tenants", "bill_width_mm"),
        ("tenants", "bill_height_mm"),
    ]
    for table, col in checks:
        names = {c["name"] for c in insp.get_columns(table)}
        print(f"{table}.{col}: {'OK' if col in names else 'MISSING'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
