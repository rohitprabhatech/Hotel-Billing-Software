"""Phase 8 SaaS / Master Admin tables (idempotent).

Revision ID: 20260818_phase8_saas
Revises: 20260814_wa_webhook_status

CREATE TABLE IF NOT EXISTS only. Does not DROP tables. Downgrade is a no-op
so a live database cannot lose Master/SaaS data via flask db downgrade.

Existing hosted DBs that were upgraded with apply_pending_schema.py should
`flask db stamp 20260818_phase8_saas` (or scripts/stamp_alembic_head.py),
not replay the full history from an empty alembic_version.
"""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import inspect, text

revision = "20260818_phase8_saas"
down_revision = "20260814_wa_webhook_status"
branch_labels = None
depends_on = None

SINGLETON_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_PLAN_ID = "33333333-3333-3333-3333-333333333333"
DEFAULT_FEATURES = [
    "Billing",
    "Item & category management",
    "Stock management & low-stock alerts",
    "Sales reports and exports",
    "Bill printing",
    "WhatsApp bill delivery",
    "Email bill delivery",
    "AI business insights (tenant-scoped)",
    "Notifications",
    "Audit logs",
    "Business dashboard",
    "24/7 technical support access",
]


def _tables(bind) -> set[str]:
    return set(inspect(bind).get_table_names())


def _has_fk(bind, table: str, name: str) -> bool:
    return any(fk.get("name") == name for fk in inspect(bind).get_foreign_keys(table) or [])


def upgrade():
    bind = op.get_bind()
    names = _tables(bind)

    if "master_admins" not in names:
        op.execute(
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

    if "registration_requests" not in names:
        op.execute(
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

    if "platform_settings" not in names:
        op.execute(
            text(
                """
                CREATE TABLE platform_settings (
                    id                    CHAR(36)     NOT NULL,
                    trial_enabled         TINYINT(1)   NOT NULL DEFAULT 1,
                    trial_days            INT          NOT NULL DEFAULT 15,
                    expiry_warning_days   INT          NOT NULL DEFAULT 5,
                    created_at            DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at            DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                         ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    CONSTRAINT chk_platform_settings_trial_days
                        CHECK (trial_days >= 1 AND trial_days <= 365),
                    CONSTRAINT chk_platform_settings_expiry_warning
                        CHECK (expiry_warning_days >= 1 AND expiry_warning_days <= 30)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
    settings_count = bind.execute(
        text("SELECT COUNT(*) FROM platform_settings WHERE id = :id"),
        {"id": SINGLETON_ID},
    ).scalar()
    if not settings_count:
        bind.execute(
            text(
                """
                INSERT INTO platform_settings
                    (id, trial_enabled, trial_days, expiry_warning_days)
                VALUES
                    (:id, 1, 15, 5)
                """
            ),
            {"id": SINGLETON_ID},
        )

    names = _tables(bind)
    if "subscription_plans" not in names:
        op.execute(
            text(
                """
                CREATE TABLE subscription_plans (
                    id              CHAR(36)       NOT NULL,
                    name            VARCHAR(120)   NOT NULL,
                    description     TEXT           NULL,
                    price           DECIMAL(12,2)  NOT NULL,
                    currency        VARCHAR(8)     NOT NULL DEFAULT 'INR',
                    billing_cycle   VARCHAR(20)    NOT NULL DEFAULT 'MONTHLY',
                    trial_eligible  TINYINT(1)     NOT NULL DEFAULT 1,
                    is_public       TINYINT(1)     NOT NULL DEFAULT 1,
                    is_active       TINYINT(1)     NOT NULL DEFAULT 1,
                    display_order   INT            NOT NULL DEFAULT 0,
                    features        JSON           NULL,
                    created_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                     ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    INDEX ix_subscription_plans_active (is_active, is_public, display_order),
                    CONSTRAINT chk_subscription_plans_cycle
                        CHECK (billing_cycle IN ('MONTHLY', 'YEARLY')),
                    CONSTRAINT chk_subscription_plans_price
                        CHECK (price >= 0)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
    plan_count = bind.execute(text("SELECT COUNT(*) FROM subscription_plans")).scalar()
    if not plan_count:
        bind.execute(
            text(
                """
                INSERT INTO subscription_plans
                    (id, name, description, price, currency, billing_cycle,
                     trial_eligible, is_public, is_active, display_order, features)
                VALUES
                    (:id, :name, :description, :price, 'INR', 'MONTHLY',
                     1, 1, 1, 1, :features)
                """
            ),
            {
                "id": DEFAULT_PLAN_ID,
                "name": "Business Billing Plan",
                "description": "Monthly Business Billing subscription.",
                "price": "550.00",
                "features": json.dumps(DEFAULT_FEATURES),
            },
        )

    names = _tables(bind)
    if "subscriptions" not in names:
        op.execute(
            text(
                """
                CREATE TABLE subscriptions (
                    id                  CHAR(36)       NOT NULL,
                    tenant_id           CHAR(36)       NOT NULL,
                    plan_id             CHAR(36)       NULL,
                    status              VARCHAR(20)    NOT NULL DEFAULT 'TRIAL',
                    starts_at           DATETIME(6)    NULL,
                    ends_at             DATETIME(6)    NULL,
                    trial_starts_at     DATETIME(6)    NULL,
                    trial_ends_at       DATETIME(6)    NULL,
                    price_at_purchase   DECIMAL(12,2)  NULL,
                    payment_status      VARCHAR(30)    NULL,
                    payment_provider    VARCHAR(40)    NULL,
                    payment_reference   VARCHAR(120)   NULL,
                    created_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at          DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                                         ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    INDEX ix_subscriptions_tenant (tenant_id),
                    INDEX ix_subscriptions_status (status),
                    INDEX ix_subscriptions_trial_ends (trial_ends_at),
                    CONSTRAINT chk_subscriptions_status
                        CHECK (status IN (
                            'TRIAL', 'ACTIVE', 'EXPIRING', 'EXPIRED',
                            'CANCELLED', 'SUSPENDED'
                        )),
                    CONSTRAINT fk_subscriptions_tenant
                        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                        ON DELETE RESTRICT ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        )
    names = _tables(bind)
    if "subscriptions" in names and not _has_fk(bind, "subscriptions", "fk_subscriptions_plan"):
        op.execute(
            text(
                """
                ALTER TABLE subscriptions
                    ADD CONSTRAINT fk_subscriptions_plan
                    FOREIGN KEY (plan_id) REFERENCES subscription_plans (id)
                    ON DELETE SET NULL ON UPDATE CASCADE
                """
            )
        )

    names = _tables(bind)
    if "subscription_notices" not in names:
        op.execute(
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

    if "platform_notifications" not in names:
        op.execute(
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

    names = _tables(bind)
    if "platform_audit_logs" not in names:
        op.execute(
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


def downgrade():
    # Intentionally empty: never DROP Master/SaaS tables from a live database.
    return
