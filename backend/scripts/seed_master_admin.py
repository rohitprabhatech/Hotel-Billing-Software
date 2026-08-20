"""Create the first Master Admin from environment variables (idempotent).

Does not overwrite an existing row. Never commit real passwords to source.

  MASTER_ADMIN_EMAIL
  MASTER_ADMIN_PASSWORD   (min 8 characters)
  MASTER_ADMIN_NAME       (optional, default: Prabha Technology Admin)

Prints the redacted database target before writing. Uses DATABASE_URL or MYSQL_*.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine, inspect

from app import create_app
from app.extensions import db
from app.services.master_bootstrap_service import MasterBootstrapService
from app.utils.database_url import load_backend_env
from app.utils.exceptions import ValidationError


def _print_target(uri: str) -> None:
    engine = create_engine(uri)
    print(
        f"target={engine.url.host or engine.dialect.name}/"
        f"{engine.url.database or '(memory)'}"
    )


def main() -> int:
    load_backend_env()
    app = create_app()
    uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    _print_target(uri)

    email = (os.environ.get("MASTER_ADMIN_EMAIL") or "").strip().lower()
    password = os.environ.get("MASTER_ADMIN_PASSWORD") or ""
    name = (os.environ.get("MASTER_ADMIN_NAME") or "Prabha Technology Admin").strip()

    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
        if "master_admins" not in tables:
            print("master_admins table is missing. Run apply_pending_schema.py first.", file=sys.stderr)
            return 1
        try:
            result = MasterBootstrapService.seed_first(email=email, password=password, name=name)
        except ValidationError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if result == "exists":
        print(f"Master admin already exists: {email}")
    else:
        print(f"Created master admin: {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
