"""Stamp alembic_version to Phase 8 head without running migrations.

Use this on a database that already received apply_pending_schema.py.
Does not CREATE/DROP tenant or billing tables.
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

PHASE8_HEAD = "20260818_phase8_saas"
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
        print(f"flask_host={configured.hostname} flask_db={configured.path}", file=sys.stderr)
        print(f"env_host={expected.hostname} env_db={expected.path}", file=sys.stderr)
        return 1
    if (configured.scheme or "").startswith("sqlite"):
        print("Refusing to stamp a SQLite database.", file=sys.stderr)
        return 1

    print(f"target={configured.hostname}/{configured.path.lstrip('/')}")
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
        missing = [name for name in PHASE8_TABLES if name not in tables]
        if missing:
            print(f"Phase 8 tables missing: {', '.join(missing)}", file=sys.stderr)
            print("Run apply_pending_schema.py before stamping.", file=sys.stderr)
            return 1
        stamp(revision=PHASE8_HEAD)
        versions = [
            row[0] for row in db.session.execute(text("SELECT version_num FROM alembic_version")).all()
        ]
    print(f"alembic_version={versions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
