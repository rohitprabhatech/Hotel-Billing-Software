"""Read-only check: Phase 8 tables + Master Admin presence on DATABASE_URL / MYSQL_*.

Exit codes:
  0 — schema complete and at least one Master Admin
  1 — schema complete, master_admins empty (seed required)
  2 — cannot connect, or Phase 8 tables missing
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine, inspect, text

from app.utils.database_url import load_backend_env, require_database_url

PHASE8_TABLES = [
    "master_admins",
    "registration_requests",
    "platform_settings",
    "subscription_plans",
    "subscriptions",
    "subscription_notices",
    "platform_notifications",
    "platform_audit_logs",
]

COUNT_TABLES = [
    "tenants",
    "users",
    "bills",
    "bill_items",
    "master_admins",
    "subscription_plans",
    "subscriptions",
]


def main() -> int:
    load_backend_env()
    try:
        url = require_database_url()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    engine = create_engine(url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    missing = [name for name in PHASE8_TABLES if name not in tables]
    counts: dict[str, int | None] = {}
    alembic_versions: list[str] = []
    with engine.connect() as conn:
        for table in COUNT_TABLES:
            if table not in tables:
                counts[table] = None
                continue
            counts[table] = int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar() or 0)
        if "alembic_version" in tables:
            alembic_versions = [
                str(row[0])
                for row in conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
            ]

    report = {
        "target": {
            "host": engine.url.host,
            "port": engine.url.port,
            "database": engine.url.database,
        },
        "table_count": len(tables),
        "phase8_missing": missing,
        "alembic_versions": alembic_versions,
        "row_counts": counts,
        "master_admin_seeded": (counts.get("master_admins") or 0) > 0,
    }
    print(json.dumps(report, indent=2))

    if missing:
        print("Phase 8 tables missing. Run apply_pending_schema.py after backup.", file=sys.stderr)
        return 2
    if not report["master_admin_seeded"]:
        print("master_admins is empty. Set MASTER_ADMIN_EMAIL / MASTER_ADMIN_PASSWORD and run seed_master_admin.py.", file=sys.stderr)
        return 1
    print("Platform ready: Phase 8 schema present and Master Admin seeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
