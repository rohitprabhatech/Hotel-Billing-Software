"""Read-only database schema inspector for Business Billing deployments.

Use this before any production upgrade. It does not create, alter, or delete
database objects. It only reads table, column, index, FK, and row-count
metadata from the DATABASE_URL target.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine, inspect, text

from app.utils.database_url import load_backend_env, require_database_url

CORE_TABLES = [
    "tenants",
    "roles",
    "users",
    "password_reset_tokens",
    "email_verification_tokens",
    "categories",
    "items",
    "bill_number_counters",
    "bills",
    "bill_items",
    "notifications",
    "tenant_whatsapp_configs",
    "bill_deliveries",
    "audit_logs",
    "stock_movements",
]

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
    "items",
    "bills",
    "bill_items",
    "notifications",
    "audit_logs",
    "stock_movements",
    "master_admins",
    "registration_requests",
    "subscription_plans",
    "subscriptions",
    "subscription_notices",
    "platform_notifications",
    "platform_audit_logs",
]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only schema and metadata inspection for DATABASE_URL."
    )
    parser.add_argument(
        "--json-out",
        help="Optional file path to write the JSON report.",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        default=None,
        help="Specific tables to include in detailed output. Defaults to core + Phase 8 tables.",
    )
    return parser


def _row_count(conn, table: str) -> int | None:
    try:
        return int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar() or 0)
    except Exception:
        return None


def _safe_text_list(rows: list[dict], *keys: str) -> list[dict]:
    result = []
    for row in rows:
        item = {}
        for key in keys:
            value = row.get(key)
            item[key] = list(value) if isinstance(value, tuple) else value
        result.append(item)
    return result


def main() -> int:
    args = _parser().parse_args()

    load_backend_env()
    try:
        url = require_database_url()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    engine = create_engine(url)
    inspector = inspect(engine)

    table_names = sorted(inspector.get_table_names())
    desired_tables = args.tables or (CORE_TABLES + PHASE8_TABLES)
    desired_tables = [name for name in desired_tables if name in table_names]

    report: dict[str, object] = {
        "database_url_present": True,
        "dialect": engine.dialect.name,
        "target": {
            "host": engine.url.host,
            "port": engine.url.port,
            "database": engine.url.database,
        },
        "table_count": len(table_names),
        "tables": table_names,
        "core_tables_present": [name for name in CORE_TABLES if name in table_names],
        "phase8_tables_present": [name for name in PHASE8_TABLES if name in table_names],
        "phase8_tables_missing": [name for name in PHASE8_TABLES if name not in table_names],
        "alembic_version_present": "alembic_version" in table_names,
        "alembic_versions": [],
        "row_counts": {},
        "table_details": {},
    }

    with engine.connect() as conn:
        if "alembic_version" in table_names:
            try:
                versions = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
                report["alembic_versions"] = [str(row[0]) for row in versions]
            except Exception as exc:  # noqa: BLE001
                report["alembic_versions"] = [f"ERROR: {exc}"]

        row_counts: dict[str, int | None] = {}
        for table in COUNT_TABLES:
            if table in table_names:
                row_counts[table] = _row_count(conn, table)
        report["row_counts"] = row_counts

    table_details: dict[str, object] = {}
    for table in desired_tables:
        columns = []
        for col in inspector.get_columns(table):
            columns.append(
                {
                    "name": col.get("name"),
                    "type": str(col.get("type")),
                    "nullable": bool(col.get("nullable")),
                    "default": None if col.get("default") is None else str(col.get("default")),
                    "primary_key": bool(col.get("primary_key")),
                }
            )
        pk = inspector.get_pk_constraint(table) or {}
        indexes = _safe_text_list(inspector.get_indexes(table) or [], "name", "column_names", "unique")
        fks = []
        for fk in inspector.get_foreign_keys(table) or []:
            fks.append(
                {
                    "name": fk.get("name"),
                    "constrained_columns": list(fk.get("constrained_columns") or []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": list(fk.get("referred_columns") or []),
                    "options": fk.get("options") or {},
                }
            )
        table_details[table] = {
            "columns": columns,
            "primary_key": list(pk.get("constrained_columns") or []),
            "indexes": indexes,
            "foreign_keys": fks,
        }
    report["table_details"] = table_details

    payload = json.dumps(report, indent=2, sort_keys=False)
    print(payload)

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")
        print(f"\nSaved report to {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
