"""Apply minimum_stock_level + notifications table (idempotent)."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def _has_column(conn, table: str, column: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                  AND COLUMN_NAME = :column
                """
            ),
            {"table": table, "column": column},
        ).scalar()
    )


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
        if not _has_column(conn, "items", "minimum_stock_level"):
            conn.execute(
                text(
                    "ALTER TABLE items ADD COLUMN minimum_stock_level DECIMAL(12,3) NULL "
                    "AFTER stock_quantity"
                )
            )
            print("Added items.minimum_stock_level")
        else:
            print("items.minimum_stock_level already exists")

        if not _has_table(conn, "notifications"):
            conn.execute(
                text(
                    """
                    CREATE TABLE notifications (
                        id            CHAR(36)     NOT NULL,
                        tenant_id     CHAR(36)     NOT NULL,
                        user_id       CHAR(36)     NULL,
                        type          VARCHAR(50)  NOT NULL,
                        title         VARCHAR(160) NOT NULL,
                        message       TEXT         NOT NULL,
                        entity_type   VARCHAR(50)  NULL,
                        entity_id     CHAR(36)     NULL,
                        is_read       TINYINT(1)   NOT NULL DEFAULT 0,
                        read_at       DATETIME(6)  NULL,
                        created_at    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        INDEX ix_notifications_tenant_created (tenant_id, created_at),
                        INDEX ix_notifications_tenant_unread (tenant_id, is_read, created_at),
                        INDEX ix_notifications_tenant_entity (tenant_id, entity_type, entity_id),
                        CONSTRAINT fk_notifications_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE,
                        CONSTRAINT fk_notifications_user
                            FOREIGN KEY (user_id) REFERENCES users (id)
                            ON DELETE SET NULL ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created notifications table")
        else:
            print("notifications table already exists")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
