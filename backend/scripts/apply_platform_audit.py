"""Create platform_audit_logs (idempotent). Never drops data."""

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
        if not _has_table(conn, "master_admins"):
            print("SKIP platform_audit_logs — master_admins table missing")
            return 0

        if _has_table(conn, "platform_audit_logs"):
            print("platform_audit_logs already exists")
            return 0

        conn.execute(
            text(
                """
                CREATE TABLE platform_audit_logs (
                    id              CHAR(36)     NOT NULL,
                    actor_id        CHAR(36)     NULL,
                    actor_name      VARCHAR(120) NULL,
                    actor_email     VARCHAR(255) NULL,
                    action          VARCHAR(50)  NOT NULL,
                    entity_type     VARCHAR(50)  NOT NULL,
                    entity_id       CHAR(36)     NULL,
                    tenant_id       CHAR(36)     NULL,
                    old_data        JSON         NULL,
                    new_data        JSON         NULL,
                    ip_address      VARCHAR(45)  NULL,
                    user_agent      VARCHAR(255) NULL,
                    created_at      DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    INDEX ix_platform_audit_logs_actor (actor_id),
                    INDEX ix_platform_audit_logs_action (action),
                    INDEX ix_platform_audit_logs_tenant (tenant_id),
                    INDEX ix_platform_audit_logs_created_at (created_at),
                    CONSTRAINT fk_platform_audit_logs_actor
                        FOREIGN KEY (actor_id) REFERENCES master_admins (id)
                        ON DELETE SET NULL ON UPDATE CASCADE,
                    CONSTRAINT fk_platform_audit_logs_tenant
                        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                        ON DELETE SET NULL ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
        print("Created platform_audit_logs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
