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

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (BACKEND_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.utils.database_url import load_backend_env, resolve_database_url

SCRIPTS = [
    "apply_saas_auth_schema.py",
    "apply_item_created_by.py",
    "apply_bill_payment_method.py",
    "apply_tenant_business_type.py",
    "apply_schema_relationship_fixes.py",
    "apply_item_catalog_fields.py",
    "apply_category_parent_key.py",
    "apply_bill_report_index.py",
    "apply_stock_notifications.py",
    "apply_whatsapp_bill_delivery.py",
    "apply_users_email_unique.py",
    "apply_whatsapp_webhook_statuses.py",
    "apply_email_bill_delivery.py",
    "apply_stock_movements.py",
    "apply_stock_receive.py",
    "apply_stock_movement_sources.py",
    "apply_perf_indexes.py",
    "apply_master_admins.py",
    "apply_registration_requests.py",
    "apply_trial_management.py",
    "apply_subscription_plans.py",
    "apply_subscription_lifecycle.py",
    "apply_expiry_notifications.py",
    "apply_platform_audit.py",
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
    load_backend_env()
    url = resolve_database_url()
    if not url:
        print(
            "DATABASE_URL or MYSQL_HOST + MYSQL_USER + MYSQL_DATABASE is required",
            file=sys.stderr,
        )
        return 1
    os.environ["DATABASE_URL"] = url

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
