"""Apply registration_requests table (idempotent)."""

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
        if _has_table(conn, "registration_requests"):
            print("registration_requests already exists")
            return 0
        conn.execute(
            text(
                """
                CREATE TABLE registration_requests (
                    id                  CHAR(36)      NOT NULL,
                    business_name       VARCHAR(200)  NOT NULL,
                    business_type       VARCHAR(40)   NOT NULL,
                    owner_name          VARCHAR(120)  NOT NULL,
                    owner_email         VARCHAR(255)  NOT NULL,
                    password_hash       VARCHAR(255)  NOT NULL,
                    mobile              VARCHAR(30)   NULL,
                    address             VARCHAR(255)  NULL,
                    city                VARCHAR(100)  NULL,
                    state               VARCHAR(100)  NULL,
                    country             VARCHAR(80)   NULL,
                    pincode             VARCHAR(20)   NULL,
                    gst_number          VARCHAR(30)   NULL,
                    fssai_number        VARCHAR(50)   NULL,
                    status              VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
                    requested_at        DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    approved_at         DATETIME(6)   NULL,
                    rejected_at         DATETIME(6)   NULL,
                    approved_by         CHAR(36)      NULL,
                    rejected_by         CHAR(36)      NULL,
                    rejection_reason    TEXT          NULL,
                    tenant_id           CHAR(36)      NULL,
                    terms_accepted_at   DATETIME(6)   NULL,
                    created_at          DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at          DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                     ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    INDEX ix_registration_requests_status (status),
                    INDEX ix_registration_requests_email (owner_email),
                    INDEX ix_registration_requests_requested (requested_at),
                    CONSTRAINT chk_registration_requests_status
                        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
                    CONSTRAINT fk_registration_requests_approved_by
                        FOREIGN KEY (approved_by) REFERENCES master_admins (id)
                        ON DELETE SET NULL ON UPDATE CASCADE,
                    CONSTRAINT fk_registration_requests_rejected_by
                        FOREIGN KEY (rejected_by) REFERENCES master_admins (id)
                        ON DELETE SET NULL ON UPDATE CASCADE,
                    CONSTRAINT fk_registration_requests_tenant
                        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                        ON DELETE SET NULL ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
        print("Created registration_requests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
