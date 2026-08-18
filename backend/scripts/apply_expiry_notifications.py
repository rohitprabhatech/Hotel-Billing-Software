"""Create subscription_notices + platform_notifications (idempotent)."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


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
        if not _has_table(conn, "subscriptions"):
            print("SKIP expiry notifications — subscriptions table missing")
            return 0

        if not _has_table(conn, "subscription_notices"):
            conn.execute(
                text(
                    """
                    CREATE TABLE subscription_notices (
                        id                  CHAR(36)       NOT NULL,
                        subscription_id     CHAR(36)       NOT NULL,
                        tenant_id           CHAR(36)       NOT NULL,
                        notice_type         VARCHAR(20)    NOT NULL,
                        period_key          VARCHAR(32)    NOT NULL,
                        created_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        UNIQUE KEY uq_subscription_notices_period
                            (subscription_id, notice_type, period_key),
                        INDEX ix_subscription_notices_tenant (tenant_id),
                        CONSTRAINT chk_subscription_notices_type
                            CHECK (notice_type IN ('EXPIRING', 'EXPIRED')),
                        CONSTRAINT fk_subscription_notices_subscription
                            FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE,
                        CONSTRAINT fk_subscription_notices_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created subscription_notices")
        else:
            print("subscription_notices already exists")

        if not _has_table(conn, "platform_notifications"):
            conn.execute(
                text(
                    """
                    CREATE TABLE platform_notifications (
                        id                  CHAR(36)       NOT NULL,
                        type                VARCHAR(50)    NOT NULL,
                        title               VARCHAR(160)   NOT NULL,
                        message             TEXT           NOT NULL,
                        entity_type         VARCHAR(50)    NULL,
                        entity_id           CHAR(36)       NULL,
                        is_read             TINYINT(1)     NOT NULL DEFAULT 0,
                        read_at             DATETIME(6)    NULL,
                        created_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        INDEX ix_platform_notifications_unread (is_read, created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created platform_notifications")
        else:
            print("platform_notifications already exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
