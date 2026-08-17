"""Ensure stock_movements allows source RECEIVE (idempotent)."""

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


def _has_check(conn, name: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'stock_movements'
                  AND CONSTRAINT_NAME = :name
                  AND CONSTRAINT_TYPE = 'CHECK'
                """
            ),
            {"name": name},
        ).scalar()
    )


_CREATE_SQL = """
CREATE TABLE stock_movements (
    id              CHAR(36)       NOT NULL,
    tenant_id       CHAR(36)       NOT NULL,
    item_id         CHAR(36)       NOT NULL,
    delta           DECIMAL(12,3)  NOT NULL,
    quantity_after  DECIMAL(12,3)  NOT NULL,
    source          VARCHAR(20)    NOT NULL,
    reason          TEXT           NULL,
    reference_type  VARCHAR(20)    NULL,
    reference_id    CHAR(36)       NULL,
    created_by      CHAR(36)       NULL,
    created_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                     ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_stock_movements_tenant_created (tenant_id, created_at),
    INDEX ix_stock_movements_tenant_item (tenant_id, item_id),
    CONSTRAINT fk_stock_movements_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_stock_movements_item
        FOREIGN KEY (item_id) REFERENCES items (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_stock_movements_user
        FOREIGN KEY (created_by) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_stock_movements_source
        CHECK (source IN ('BILL', 'CANCEL', 'ADJUST', 'ITEM_UPDATE', 'RECEIVE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_table(conn, "stock_movements"):
            conn.execute(text(_CREATE_SQL))
            print("Created stock_movements with RECEIVE")
            return 0

        if _has_check(conn, "chk_stock_movements_source"):
            conn.execute(text("ALTER TABLE stock_movements DROP CHECK chk_stock_movements_source"))
        conn.execute(
            text(
                """
                ALTER TABLE stock_movements
                ADD CONSTRAINT chk_stock_movements_source
                CHECK (source IN ('BILL', 'CANCEL', 'ADJUST', 'ITEM_UPDATE', 'RECEIVE'))
                """
            )
        )
        print("stock_movements source CHECK includes RECEIVE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
