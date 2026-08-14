"""Apply WhatsApp bill delivery schema (idempotent)."""

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
        for column, ddl in [
            ("customer_name", "ALTER TABLE bills ADD COLUMN customer_name VARCHAR(120) NULL AFTER table_number"),
            (
                "customer_phone_country_code",
                "ALTER TABLE bills ADD COLUMN customer_phone_country_code VARCHAR(8) NULL AFTER customer_name",
            ),
            (
                "customer_phone_national",
                "ALTER TABLE bills ADD COLUMN customer_phone_national VARCHAR(20) NULL AFTER customer_phone_country_code",
            ),
            (
                "customer_phone_e164",
                "ALTER TABLE bills ADD COLUMN customer_phone_e164 VARCHAR(20) NULL AFTER customer_phone_national",
            ),
        ]:
            if not _has_column(conn, "bills", column):
                conn.execute(text(ddl))
                print(f"Added bills.{column}")
            else:
                print(f"bills.{column} already exists")

        if not _has_table(conn, "tenant_whatsapp_configs"):
            conn.execute(
                text(
                    """
                    CREATE TABLE tenant_whatsapp_configs (
                        tenant_id               CHAR(36)     NOT NULL,
                        phone_number_id         VARCHAR(64)  NULL,
                        waba_id                 VARCHAR(64)  NULL,
                        display_phone_e164      VARCHAR(20)  NULL,
                        access_token_encrypted  TEXT         NULL,
                        template_name           VARCHAR(120) NULL,
                        template_language       VARCHAR(20)  NOT NULL DEFAULT 'en',
                        is_enabled              TINYINT(1)   NOT NULL DEFAULT 0,
                        connected_at            DATETIME(6)  NULL,
                        created_at              DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at              DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (tenant_id),
                        CONSTRAINT fk_tenant_whatsapp_configs_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created tenant_whatsapp_configs")
        else:
            print("tenant_whatsapp_configs already exists")

        if not _has_table(conn, "bill_deliveries"):
            conn.execute(
                text(
                    """
                    CREATE TABLE bill_deliveries (
                        id                        CHAR(36)     NOT NULL,
                        tenant_id                 CHAR(36)     NOT NULL,
                        bill_id                   CHAR(36)     NOT NULL,
                        delivery_method           VARCHAR(20)  NOT NULL,
                        recipient_phone_e164      VARCHAR(20)  NULL,
                        recipient_phone_masked    VARCHAR(32)  NULL,
                        status                    VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
                        provider_message_id       VARCHAR(120) NULL,
                        error_message             TEXT         NULL,
                        attempted_by              CHAR(36)     NULL,
                        sent_at                   DATETIME(6)  NULL,
                        created_at                DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at                DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                             ON UPDATE CURRENT_TIMESTAMP(6),
                        PRIMARY KEY (id),
                        INDEX ix_bill_deliveries_tenant_bill (tenant_id, bill_id),
                        INDEX ix_bill_deliveries_tenant_created (tenant_id, created_at),
                        CONSTRAINT fk_bill_deliveries_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE,
                        CONSTRAINT fk_bill_deliveries_bill
                            FOREIGN KEY (bill_id) REFERENCES bills (id)
                            ON DELETE RESTRICT ON UPDATE CASCADE,
                        CONSTRAINT fk_bill_deliveries_user
                            FOREIGN KEY (attempted_by) REFERENCES users (id)
                            ON DELETE SET NULL ON UPDATE CASCADE,
                        CONSTRAINT chk_bill_deliveries_method
                            CHECK (delivery_method IN ('WHATSAPP', 'PRINT')),
                        CONSTRAINT chk_bill_deliveries_status
                            CHECK (status IN ('PENDING', 'SENT', 'FAILED'))
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
            )
            print("Created bill_deliveries")
        else:
            print("bill_deliveries already exists")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
