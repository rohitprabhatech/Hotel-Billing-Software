"""Read-only logical dump of the DATABASE_URL / MYSQL_* target.

Writes JSON (schema CREATE statements + rows) under backend/backups/.
Does not ALTER, DROP, or INSERT. Do not commit dump files (they contain hashes).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine, inspect, text

from app.utils.database_url import load_backend_env, require_database_url


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only JSON dump of the configured MySQL database.")
    parser.add_argument(
        "--out-dir",
        default=str(BACKEND_ROOT / "backups"),
        help="Directory for dump files (default: backend/backups).",
    )
    args = parser.parse_args()

    load_backend_env()
    try:
        url = require_database_url()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    engine = create_engine(url)
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    database = engine.url.database or "unknown"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stamp}-{database}.json"

    payload = {
        "taken_at_utc": stamp,
        "target": {
            "host": engine.url.host,
            "port": engine.url.port,
            "database": database,
            "dialect": engine.dialect.name,
        },
        "table_count": len(tables),
        "tables": {},
    }

    with engine.connect() as conn:
        for table in tables:
            create_row = conn.execute(text(f"SHOW CREATE TABLE `{table}`")).fetchone()
            create_sql = create_row[1] if create_row is not None else None
            col_names = [col["name"] for col in inspector.get_columns(table)]
            rows = conn.execute(text(f"SELECT * FROM `{table}`")).fetchall()
            payload["tables"][table] = {
                "create_sql": create_sql,
                "row_count": len(rows),
                "columns": col_names,
                "rows": [{col_names[i]: _jsonable(row[i]) for i in range(len(col_names))} for row in rows],
            }

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"backup_path={out_path}")
    print(f"target={engine.url.host}/{database}")
    print(f"table_count={len(tables)}")
    for table in tables:
        print(f"  {table}={payload['tables'][table]['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
