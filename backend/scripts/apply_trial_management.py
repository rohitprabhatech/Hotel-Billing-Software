"""Apply platform_settings + subscriptions (idempotent)."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text

SINGLETON_ID = "00000000-0000-0000-0000-000000000001"


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


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_table(conn, "platform_settings"):
            conn.execute(
                text(
                    """
                    CREATE TABLE platform_settings (
                        id                    CHAR(36)     NOT NULL,
                        trial_enabled         TINYINT(1)   NOT NULL DEFAULT 1,
                        trial_days            INT          NOT NULL DEFAULT 15,
                        expiry_warning_days   INT          NOT NULL DEFAULT 5,
                        created_at            DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at            DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        CONSTRAINT chk_platform_settings_trial_days
                            CHECK (trial_days >= 1 AND trial_days <= 365),
                        CONSTRAINT chk_platform_settings_expiry_warning
                            CHECK (expiry_warning_days >= 1 AND expiry_warning_days <= 30)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created platform_settings")
        else:
            print("platform_settings already exists")

        exists = conn.execute(
            text("SELECT COUNT(*) FROM platform_settings WHERE id = :id"),
            {"id": SINGLETON_ID},
        ).scalar()
        if not exists:
            conn.execute(
                text(
                    """
                    INSERT INTO platform_settings
                        (id, trial_enabled, trial_days, expiry_warning_days)
                    VALUES
                        (:id, 1, 15, 5)
                    """
                ),
                {"id": SINGLETON_ID},
            )
            print("Seeded platform_settings singleton (trial 15 days ON)")

        if not _has_table(conn, "subscriptions"):
            conn.execute(
                text(
                    """
                    CREATE TABLE subscriptions (
                        id                  CHAR(36)       NOT NULL,
                        tenant_id           CHAR(36)       NOT NULL,
                        plan_id             CHAR(36)       NULL,
                        status              VARCHAR(20)    NOT NULL DEFAULT 'TRIAL',
                        starts_at           DATETIME(6)    NULL,
                        ends_at             DATETIME(6)    NULL,
                        trial_starts_at     DATETIME(6)    NULL,
                        trial_ends_at       DATETIME(6)    NULL,
                        price_at_purchase   DECIMAL(12,2)  NULL,
                        payment_status      VARCHAR(30)    NULL,
                        payment_provider    VARCHAR(40)    NULL,
                        payment_reference   VARCHAR(120)   NULL,
                        created_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        INDEX ix_subscriptions_tenant (tenant_id),
                        INDEX ix_subscriptions_status (status),
                        INDEX ix_subscriptions_trial_ends (trial_ends_at),
                        CONSTRAINT chk_subscriptions_status
                            CHECK (status IN (
                                'TRIAL', 'ACTIVE', 'EXPIRING', 'EXPIRED',
                                'CANCELLED', 'SUSPENDED'
                            )),
                        CONSTRAINT fk_subscriptions_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created subscriptions")
        else:
            print("subscriptions already exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
