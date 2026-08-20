"""Apply email bill delivery schema (idempotent)."""

from __future__ import annotations

import os
import sys

from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sqlalchemy import create_engine, text

from schema_helpers import check_clause, drop_check_constraint


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
    if drop_check_constraint(conn, "bill_deliveries", name):
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

        clause = check_clause(conn, "chk_bill_deliveries_method") or ""
        if "EMAIL" in clause.upper():
            print("chk_bill_deliveries_method already includes EMAIL")
        else:
            _drop_check_if_exists(conn, "chk_bill_deliveries_method")
            try:
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
            except Exception as exc:
                print(f"CHECK constraint note: {exc}")

    print("Email bill delivery schema applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
