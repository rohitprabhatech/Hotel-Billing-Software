"""Apply email bill delivery schema (idempotent)."""

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


def _drop_check_if_exists(conn, name: str) -> None:
    exists = conn.execute(
        text(
            """
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'bill_deliveries'
              AND CONSTRAINT_NAME = :name
              AND CONSTRAINT_TYPE = 'CHECK'
            """
        ),
        {"name": name},
    ).scalar()
    if exists:
        conn.execute(text(f"ALTER TABLE bill_deliveries DROP CHECK {name}"))
        print(f"Dropped check {name}")


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if not _has_column(conn, "bills", "customer_email"):
            conn.execute(
                text(
                    "ALTER TABLE bills ADD COLUMN customer_email VARCHAR(255) NULL "
                    "AFTER customer_phone_e164"
                )
            )
            print("Added bills.customer_email")
        else:
            print("bills.customer_email already exists")

        if not _has_column(conn, "bill_deliveries", "recipient_email"):
            conn.execute(
                text(
                    "ALTER TABLE bill_deliveries ADD COLUMN recipient_email VARCHAR(255) NULL "
                    "AFTER recipient_phone_masked"
                )
            )
            print("Added bill_deliveries.recipient_email")
        else:
            print("bill_deliveries.recipient_email already exists")

        if not _has_column(conn, "bill_deliveries", "recipient_email_masked"):
            conn.execute(
                text(
                    "ALTER TABLE bill_deliveries ADD COLUMN recipient_email_masked VARCHAR(64) NULL "
                    "AFTER recipient_email"
                )
            )
            print("Added bill_deliveries.recipient_email_masked")
        else:
            print("bill_deliveries.recipient_email_masked already exists")

        _drop_check_if_exists(conn, "chk_bill_deliveries_method")
        conn.execute(
            text(
                """
                ALTER TABLE bill_deliveries
                ADD CONSTRAINT chk_bill_deliveries_method
                CHECK (delivery_method IN ('WHATSAPP', 'PRINT', 'EMAIL'))
                """
            )
        )
        print("Updated chk_bill_deliveries_method to include EMAIL")

    print("Email bill delivery schema applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
