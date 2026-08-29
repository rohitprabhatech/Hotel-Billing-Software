"""Validate cafe billing schema on DATABASE_URL (read-only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db

REQUIRED = {
    "coupons": {
        "id",
        "tenant_id",
        "code",
        "discount_type",
        "discount_value",
        "usage_count",
        "is_active",
    },
    "coupon_redemptions": {
        "id",
        "tenant_id",
        "coupon_id",
        "bill_id",
        "order_id",
        "discount_applied",
    },
    "item_addons": {"id", "tenant_id", "group_id", "linked_item_id", "extra_price"},
    "bills": {"coupon_id", "coupon_code", "coupon_discount"},
    "order_item_addons": {"id", "tenant_id", "order_item_id", "addon_id"},
}


def main() -> int:
    app = create_app("development")
    with app.app_context():
        insp = inspect(db.engine)
        missing_tables: list[str] = []
        missing_columns: dict[str, list[str]] = {}
        for table, cols in REQUIRED.items():
            if table not in insp.get_table_names():
                missing_tables.append(table)
                continue
            present = {c["name"] for c in insp.get_columns(table)}
            absent = sorted(cols - present)
            if absent:
                missing_columns[table] = absent

        stock_check = None
        if "stock_movements" in insp.get_table_names():
            row = db.session.execute(
                text(
                    """
                    SELECT CHECK_CLAUSE
                    FROM information_schema.CHECK_CONSTRAINTS
                    WHERE CONSTRAINT_SCHEMA = DATABASE()
                      AND CONSTRAINT_NAME = 'chk_stock_movements_source'
                    """
                )
            ).fetchone()
            stock_check = row[0] if row else None

        recipe_ok = "RECIPE" in (stock_check or "").upper()
        report = {
            "missing_tables": missing_tables,
            "missing_columns": missing_columns,
            "stock_movement_check_has_recipe": recipe_ok,
            "alembic_head_expected": "20260827_cafe_coupons",
        }
        print(json.dumps(report, indent=2))
        if missing_tables or missing_columns or not recipe_ok:
            return 2
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
