"""Apply master_admins platform table (idempotent)."""

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
        if _has_table(conn, "master_admins"):
            print("master_admins already exists")
            return 0
        conn.execute(
            text(
                """
                CREATE TABLE master_admins (
                    id              CHAR(36)      NOT NULL,
                    name            VARCHAR(120)  NOT NULL,
                    email           VARCHAR(255)  NOT NULL,
                    password_hash   VARCHAR(255)  NOT NULL,
                    is_active       TINYINT(1)    NOT NULL DEFAULT 1,
                    token_version   INT           NOT NULL DEFAULT 0,
                    last_login_at   DATETIME(6)   NULL,
                    created_at      DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at      DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                     ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    UNIQUE KEY uq_master_admins_email (email),
                    INDEX ix_master_admins_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
        print("Created master_admins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
