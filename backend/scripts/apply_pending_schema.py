"""Apply all pending incremental schema upgrades in order (idempotent helpers).

Prefer this for existing MySQL databases that were created from older SQL dumps.

Fresh installs should use:
  sql/01_create_database.sql
  sql/02_schema.sql

Alembic path (if enabled):
  flask db upgrade
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

SCRIPTS = [
    "apply_saas_auth_schema.py",
    "apply_item_created_by.py",
    "apply_bill_payment_method.py",
    "apply_tenant_business_type.py",
    "apply_schema_relationship_fixes.py",
    "apply_item_catalog_fields.py",
]


def _run_script(path: Path) -> int:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        print(f"Unable to load {path}", file=sys.stderr)
        return 1
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "main"):
        return int(module.main() or 0)
    print(f"No main() in {path}", file=sys.stderr)
    return 1


def main() -> int:
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parent
    for name in SCRIPTS:
        path = root / name
        if not path.exists():
            print(f"SKIP missing {name}")
            continue
        print(f"=== {name} ===")
        code = _run_script(path)
        if code != 0:
            print(f"FAILED: {name} exited {code}", file=sys.stderr)
            return code
    print("All pending schema helpers applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
