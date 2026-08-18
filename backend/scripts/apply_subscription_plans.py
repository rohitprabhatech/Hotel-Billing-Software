"""Apply subscription_plans and subscriptions.plan_id FK (idempotent)."""

from __future__ import annotations

import json
import os
import sys

from sqlalchemy import create_engine, text

DEFAULT_PLAN_ID = "33333333-3333-3333-3333-333333333333"
DEFAULT_FEATURES = [
    "Billing",
    "Item & category management",
    "Stock management & low-stock alerts",
    "Sales reports and exports",
    "Bill printing",
    "WhatsApp bill delivery",
    "Email bill delivery",
    "AI business insights (tenant-scoped)",
    "Notifications",
    "Audit logs",
    "Business dashboard",
    "24/7 technical support access",
]


def _has_table(conn, table: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                """
            ),
            {"table": table},
        ).scalar()
    )


def _has_fk(conn, name: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'subscriptions'
                  AND CONSTRAINT_NAME = :name
                  AND CONSTRAINT_TYPE = 'FOREIGN KEY'
                """
            ),
            {"name": name},
        ).scalar()
    )


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_table(conn, "subscription_plans"):
            conn.execute(
                text(
                    """
                    CREATE TABLE subscription_plans (
                        id              CHAR(36)       NOT NULL,
                        name            VARCHAR(120)   NOT NULL,
                        description     TEXT           NULL,
                        price           DECIMAL(12,2)  NOT NULL,
                        currency        VARCHAR(8)     NOT NULL DEFAULT 'INR',
                        billing_cycle   VARCHAR(20)    NOT NULL DEFAULT 'MONTHLY',
                        trial_eligible  TINYINT(1)     NOT NULL DEFAULT 1,
                        is_public       TINYINT(1)     NOT NULL DEFAULT 1,
                        is_active       TINYINT(1)     NOT NULL DEFAULT 1,
                        display_order   INT            NOT NULL DEFAULT 0,
                        features        JSON           NULL,
                        created_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                         ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        INDEX ix_subscription_plans_active (is_active, is_public, display_order),
                        CONSTRAINT chk_subscription_plans_cycle
                            CHECK (billing_cycle IN ('MONTHLY', 'YEARLY')),
                        CONSTRAINT chk_subscription_plans_price
                            CHECK (price >= 0)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created subscription_plans")
        else:
            print("subscription_plans already exists")

        count = conn.execute(text("SELECT COUNT(*) FROM subscription_plans")).scalar()
        if not count:
            conn.execute(
                text(
                    """
                    INSERT INTO subscription_plans
                        (id, name, description, price, currency, billing_cycle,
                         trial_eligible, is_public, is_active, display_order, features)
                    VALUES
                        (:id, :name, :description, :price, 'INR', 'MONTHLY',
                         1, 1, 1, 1, CAST(:features AS JSON))
                    """
                ),
                {
                    "id": DEFAULT_PLAN_ID,
                    "name": "Business Billing Plan",
                    "description": "Monthly Business Billing subscription.",
                    "price": "550.00",
                    "features": json.dumps(DEFAULT_FEATURES),
                },
            )
            print("Seeded default Business Billing Plan (₹550 / month)")

        if _has_table(conn, "subscriptions") and not _has_fk(conn, "fk_subscriptions_plan"):
            conn.execute(
                text(
                    """
                    ALTER TABLE subscriptions
                        ADD CONSTRAINT fk_subscriptions_plan
                        FOREIGN KEY (plan_id) REFERENCES subscription_plans (id)
                        ON DELETE SET NULL ON UPDATE CASCADE
                    """
                )
            )
            print("Added subscriptions.plan_id FK")
        elif not _has_table(conn, "subscriptions"):
            print("SKIP plan FK — subscriptions table missing")
        else:
            print("subscriptions.plan_id FK already present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
