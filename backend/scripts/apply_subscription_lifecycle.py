"""Grandfather tenants that have no subscription (idempotent)."""

from __future__ import annotations

import os
import sys
from uuid import uuid4

from sqlalchemy import create_engine, text

DEFAULT_PLAN_ID = "33333333-3333-3333-3333-333333333333"


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'subscriptions'
                """
            )
        ).scalar():
            print("SKIP grandfather — subscriptions table missing")
            return 0

        plan_id = None
        if conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'subscription_plans'
                """
            )
        ).scalar():
            exists = conn.execute(
                text("SELECT id FROM subscription_plans WHERE id = :id"),
                {"id": DEFAULT_PLAN_ID},
            ).scalar()
            plan_id = exists

        rows = conn.execute(
            text(
                """
                SELECT t.id
                FROM tenants t
                WHERE NOT EXISTS (
                    SELECT 1 FROM subscriptions s WHERE s.tenant_id = t.id
                )
                """
            )
        ).fetchall()
        granted = 0
        for (tenant_id,) in rows:
            conn.execute(
                text(
                    """
                    INSERT INTO subscriptions
                        (id, tenant_id, plan_id, status, starts_at, ends_at, payment_status)
                    VALUES
                        (:id, :tenant_id, :plan_id, 'ACTIVE', UTC_TIMESTAMP(6), NULL, 'COMPLIMENTARY')
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": tenant_id,
                    "plan_id": plan_id,
                },
            )
            granted += 1
        print(f"Granted complimentary access to {granted} tenant(s) without a subscription")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
