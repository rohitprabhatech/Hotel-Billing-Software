#!/usr/bin/env python3
"""Read-only database integrity report — does NOT delete or fix data.

Usage:
  cd backend
  DATABASE_URL=mysql+pymysql://... python scripts/validate_database_integrity.py

Reports:
  - Duplicate bill numbers per tenant
  - Bills with missing tenant_id
  - Orphan bill_items (bill missing)
  - Negative stock on tracked items
  - Finalized bills with zero items
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, text

from app import create_app
from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.item import Item


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> int:
    app = create_app(os.getenv("FLASK_ENV", "development"))
    issues = 0

    with app.app_context():
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        print(f"Target: {uri.split('@')[-1] if '@' in uri else uri}")

        section("Duplicate bill numbers (same tenant)")
        rows = db.session.execute(
            text(
                """
                SELECT tenant_id, bill_number, COUNT(*) AS cnt
                FROM bills
                GROUP BY tenant_id, bill_number
                HAVING cnt > 1
                LIMIT 50
                """
            )
        ).fetchall()
        if not rows:
            print("OK — none found")
        else:
            issues += len(rows)
            for row in rows:
                print(f"  tenant={row.tenant_id} bill_number={row.bill_number} count={row.cnt}")

        section("Bills without tenant_id")
        missing_tenant = db.session.query(Bill).filter(Bill.tenant_id.is_(None)).count()
        if missing_tenant:
            issues += missing_tenant
            print(f"FAIL — {missing_tenant} row(s)")
        else:
            print("OK")

        section("Orphan bill_items (bill deleted/missing)")
        orphan_items = db.session.execute(
            text(
                """
                SELECT bi.id, bi.bill_id
                FROM bill_items bi
                LEFT JOIN bills b ON b.id = bi.bill_id
                WHERE b.id IS NULL
                LIMIT 50
                """
            )
        ).fetchall()
        if not orphan_items:
            print("OK")
        else:
            issues += len(orphan_items)
            for row in orphan_items:
                print(f"  bill_item={row.id} missing bill={row.bill_id}")

        section("Negative stock (tracked items)")
        neg = (
            db.session.query(Item.id, Item.name, Item.stock_quantity, Item.tenant_id)
            .filter(Item.stock_quantity.isnot(None), Item.stock_quantity < 0)
            .limit(50)
            .all()
        )
        if not neg:
            print("OK")
        else:
            issues += len(neg)
            for item in neg:
                print(f"  item={item.id} name={item.name!r} stock={item.stock_quantity} tenant={item.tenant_id}")

        section("Finalized bills with no line items")
        empty_bills = db.session.execute(
            text(
                """
                SELECT b.id, b.bill_number, b.tenant_id
                FROM bills b
                LEFT JOIN bill_items bi ON bi.bill_id = b.id
                WHERE b.status = 'FINALIZED'
                GROUP BY b.id, b.bill_number, b.tenant_id
                HAVING COUNT(bi.id) = 0
                LIMIT 50
                """
            )
        ).fetchall()
        if not empty_bills:
            print("OK")
        else:
            issues += len(empty_bills)
            for row in empty_bills:
                print(f"  bill={row.id} #{row.bill_number} tenant={row.tenant_id}")

        section("Summary")
        if issues:
            print(f"ISSUES REPORTED: {issues} (review manually — no auto-fix)")
            return 1
        print("No issues detected in sampled checks.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
