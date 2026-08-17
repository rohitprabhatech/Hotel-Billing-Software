"""Apply tenants.business_type without full Alembic (dev/ops helper)."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        exists = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'tenants'
                  AND COLUMN_NAME = 'business_type'
                """
            )
        ).scalar()
        if exists:
            print("tenants.business_type already exists")
            return 0

        conn.execute(
            text(
                """
                ALTER TABLE tenants
                ADD COLUMN business_type VARCHAR(40) NOT NULL DEFAULT 'other'
                AFTER business_name
                """
            )
        )
        conn.execute(
            text("CREATE INDEX ix_tenants_business_type ON tenants (business_type)")
        )
        print("Added tenants.business_type")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
