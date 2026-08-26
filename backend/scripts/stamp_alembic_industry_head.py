"""Stamp alembic_version to industry head after schema is already applied.

Prefer `flask db upgrade` on staging/prod when the DB is Alembic-managed.
Use this stamp only when:
  - industry tables already exist (upgrade applied or greenfield 02_schema), and
  - you need to align alembic_version without re-running CREATE.

Does not DROP tables. Refuses SQLite and URI mismatch.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from flask_migrate import stamp
from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.utils.database_url import load_backend_env, require_database_url

INDUSTRY_HEAD = "20260826_biz66_perf_indexes"

# Representative tables introduced across industry packs (presence check).
REQUIRED_TABLES = [
    "customers",
    "serial_units",
    "warehouses",
    "warehouse_stocks",
    "quotations",
    "delivery_challans",
    "custom_orders",
    "price_lists",
    "sales_orders",
    "purchase_orders",
    "tour_packages",
    "travel_bookings",
    "travel_agents",
]


def main() -> int:
    load_backend_env()
    os.environ["FLASK_ENV"] = "development"
    try:
        url = require_database_url()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    expected = urlparse(url)
    app = create_app("development")
    configured = urlparse(app.config.get("SQLALCHEMY_DATABASE_URI") or "")
    if configured.hostname != expected.hostname or configured.path != expected.path:
        print(
            "Refusing to stamp: Flask URI target does not match MYSQL_*/DATABASE_URL.",
            file=sys.stderr,
        )
        return 1
    if (configured.scheme or "").startswith("sqlite"):
        print("Refusing to stamp a SQLite database.", file=sys.stderr)
        return 1

    print(f"target={configured.hostname}/{configured.path.lstrip('/')}")
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
        missing = [name for name in REQUIRED_TABLES if name not in tables]
        if missing:
            print(f"Industry tables missing: {', '.join(missing)}", file=sys.stderr)
            print("Run flask db upgrade (or restore) before stamping industry head.", file=sys.stderr)
            return 1
        stamp(revision=INDUSTRY_HEAD)
        versions = [
            row[0]
            for row in db.session.execute(text("SELECT version_num FROM alembic_version")).all()
        ]
    print(f"alembic_version={versions}")
    print(f"stamped={INDUSTRY_HEAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
