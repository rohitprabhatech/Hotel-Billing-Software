-- =============================================================================
-- Business Billing Software — MySQL Schema (Multi-Tenant)
-- Database : hotel_billing  (legacy DB name; product is multi-business)
-- Charset  : utf8mb4
-- Tool tip : Open/run this file in DBeaver against the hotel_billing connection
-- =============================================================================

USE hotel_billing;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- Drop in dependency order (safe re-run for local/dev)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS bill_deliveries;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS stock_movements;
DROP TABLE IF EXISTS tenant_whatsapp_configs;
DROP TABLE IF EXISTS bill_items;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS bill_number_counters;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS email_verification_tokens;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS tenants;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- tenants
-- -----------------------------------------------------------------------------
CREATE TABLE tenants (
    id                    CHAR(36)       NOT NULL,
    name                  VARCHAR(120)   NOT NULL,
    business_name         VARCHAR(200)   NOT NULL,
    business_type         VARCHAR(40)    NOT NULL DEFAULT 'other',
    address               VARCHAR(255)   NULL,
    city                  VARCHAR(100)   NULL,
    state                 VARCHAR(100)   NULL,
    pincode               VARCHAR(20)    NULL,
    phone                 VARCHAR(30)    NULL,
    email                 VARCHAR(255)   NULL,
    gst_number            VARCHAR(30)    NULL,
    fssai_number          VARCHAR(50)    NULL,
    bill_number_prefix    VARCHAR(20)    NULL,
    default_gst_percent   DECIMAL(5,2)   NULL,
    status                VARCHAR(20)    NOT NULL DEFAULT 'ACTIVE',
    created_at            DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at            DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    CONSTRAINT chk_tenants_status CHECK (status IN ('ACTIVE', 'SUSPENDED')),
    INDEX ix_tenants_status (status),
    INDEX ix_tenants_business_name (business_name),
    INDEX ix_tenants_business_type (business_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- roles (global — OWNER, BILLING_USER only)
-- -----------------------------------------------------------------------------
CREATE TABLE roles (
    id           CHAR(36)     NOT NULL,
    name         VARCHAR(50)  NOT NULL,
    description  VARCHAR(255) NULL,
    created_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_name (name),
    CONSTRAINT chk_roles_name CHECK (name IN ('OWNER', 'BILLING_USER'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- users (tenant-scoped)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id                   CHAR(36)      NOT NULL,
    tenant_id            CHAR(36)      NOT NULL,
    role_id              CHAR(36)      NOT NULL,
    name                 VARCHAR(120)  NOT NULL,
    email                VARCHAR(255)  NOT NULL,
    password_hash        VARCHAR(255)  NOT NULL,
    is_active            TINYINT(1)    NOT NULL DEFAULT 1,
    email_verified       TINYINT(1)    NOT NULL DEFAULT 0,
    email_verified_at    DATETIME(6)   NULL,
    password_changed_at  DATETIME(6)   NULL,
    pending_email        VARCHAR(255)  NULL,
    token_version        INT           NOT NULL DEFAULT 0,
    last_login_at        DATETIME(6)   NULL,
    created_at           DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at           DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_tenant_email (tenant_id, email),
    UNIQUE KEY uq_users_email (email),
    INDEX ix_users_tenant_id (tenant_id),
    INDEX ix_users_tenant_role (tenant_id, role_id),
    INDEX ix_users_tenant_active (tenant_id, is_active),
    CONSTRAINT fk_users_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- password_reset_tokens
-- -----------------------------------------------------------------------------
CREATE TABLE password_reset_tokens (
    id           CHAR(36)     NOT NULL,
    user_id      CHAR(36)     NOT NULL,
    token_hash   CHAR(64)     NOT NULL,
    expires_at   DATETIME(6)  NOT NULL,
    used_at      DATETIME(6)  NULL,
    created_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_password_reset_token_hash (token_hash),
    INDEX ix_password_reset_user_id (user_id),
    CONSTRAINT fk_password_reset_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- email_verification_tokens
-- -----------------------------------------------------------------------------
CREATE TABLE email_verification_tokens (
    id           CHAR(36)     NOT NULL,
    user_id      CHAR(36)     NOT NULL,
    token_hash   CHAR(64)     NOT NULL,
    purpose      VARCHAR(40)  NOT NULL DEFAULT 'signup',
    new_email    VARCHAR(255) NULL,
    expires_at   DATETIME(6)  NOT NULL,
    verified_at  DATETIME(6)  NULL,
    created_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_email_verification_token_hash (token_hash),
    INDEX ix_email_verification_user_id (user_id),
    CONSTRAINT fk_email_verification_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- categories (tenant-scoped, optional parent for subcategory)
-- -----------------------------------------------------------------------------
CREATE TABLE categories (
    id           CHAR(36)     NOT NULL,
    tenant_id    CHAR(36)     NOT NULL,
    parent_id    CHAR(36)     NULL,
    -- Coalesce NULL parent_id so main-category names are unique per tenant
    -- (MySQL UNIQUE ignores NULL duplicates in multi-column unique keys).
    parent_key   CHAR(36)     GENERATED ALWAYS AS (IFNULL(parent_id, '')) VIRTUAL,
    name         VARCHAR(120) NOT NULL,
    description  TEXT         NULL,
    is_active    TINYINT(1)   NOT NULL DEFAULT 1,
    created_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_tenant_parent_key_name (tenant_id, parent_key, name),
    INDEX ix_categories_tenant_id (tenant_id),
    INDEX ix_categories_tenant_active (tenant_id, is_active),
    INDEX ix_categories_parent_id (parent_id),
    CONSTRAINT fk_categories_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id) REFERENCES categories (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- items (tenant-scoped; deactivate instead of delete)
-- -----------------------------------------------------------------------------
CREATE TABLE items (
    id               CHAR(36)       NOT NULL,
    tenant_id        CHAR(36)       NOT NULL,
    category_id      CHAR(36)       NOT NULL,
    created_by       CHAR(36)       NULL,
    name             VARCHAR(200)   NOT NULL,
    sku              VARCHAR(64)    NULL,
    description      TEXT           NULL,
    price            DECIMAL(12,2)  NOT NULL,
    cost_price       DECIMAL(12,2)  NULL,
    gst_percentage   DECIMAL(5,2)   NOT NULL DEFAULT 0.00,
    stock_quantity   DECIMAL(12,3)  NULL,
    minimum_stock_level DECIMAL(12,3) NULL,
    is_active        TINYINT(1)     NOT NULL DEFAULT 1,
    created_at       DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at       DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_items_tenant_name (tenant_id, name),
    UNIQUE KEY uq_items_tenant_sku (tenant_id, sku),
    INDEX ix_items_tenant_id (tenant_id),
    INDEX ix_items_tenant_category (tenant_id, category_id),
    INDEX ix_items_tenant_active (tenant_id, is_active),
    INDEX ix_items_tenant_name (tenant_id, name),
    INDEX ix_items_tenant_sku (tenant_id, sku),
    INDEX ix_items_created_by (created_by),
    CONSTRAINT fk_items_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_items_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_items_created_by
        FOREIGN KEY (created_by) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_items_price CHECK (price >= 0),
    CONSTRAINT chk_items_cost_price CHECK (cost_price IS NULL OR cost_price >= 0),
    CONSTRAINT chk_items_stock CHECK (stock_quantity IS NULL OR stock_quantity >= 0),
    CONSTRAINT chk_items_min_stock CHECK (minimum_stock_level IS NULL OR minimum_stock_level >= 0),
    CONSTRAINT chk_items_gst CHECK (gst_percentage >= 0 AND gst_percentage <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- bill_number_counters (per-tenant sequence for concurrent safe bill numbers)
-- -----------------------------------------------------------------------------
CREATE TABLE bill_number_counters (
    tenant_id    CHAR(36)    NOT NULL,
    next_value   BIGINT      NOT NULL DEFAULT 1,
    updated_at   DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (tenant_id),
    CONSTRAINT fk_bill_number_counters_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_bill_number_counters_next CHECK (next_value >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- bills (historical financial records — cancel/void, never hard-delete via app)
-- -----------------------------------------------------------------------------
CREATE TABLE bills (
    id                    CHAR(36)       NOT NULL,
    tenant_id             CHAR(36)       NOT NULL,
    bill_number           VARCHAR(50)    NOT NULL,
    bill_sequence         BIGINT         NOT NULL,
    table_number          VARCHAR(30)    NULL,  -- bill reference (table/counter/token/note)
    customer_name         VARCHAR(120)   NULL,
    customer_phone_country_code VARCHAR(8) NULL,
    customer_phone_national VARCHAR(20)  NULL,
    customer_phone_e164   VARCHAR(20)    NULL,
    customer_email        VARCHAR(255)   NULL,
    subtotal              DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    discount              DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    taxable_amount        DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    cgst_amount           DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    sgst_amount           DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    gst_amount            DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    grand_total           DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    round_off             DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    status                VARCHAR(20)    NOT NULL DEFAULT 'FINALIZED',
    payment_method        VARCHAR(20)    NOT NULL DEFAULT 'cash',
    created_by            CHAR(36)       NOT NULL,
    cancelled_by          CHAR(36)       NULL,
    cancelled_at          DATETIME(6)    NULL,
    cancellation_reason   TEXT           NULL,
    printed_count         INT            NOT NULL DEFAULT 0,
    created_at            DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at            DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_bills_tenant_bill_number (tenant_id, bill_number),
    UNIQUE KEY uq_bills_tenant_bill_sequence (tenant_id, bill_sequence),
    INDEX ix_bills_tenant_created_at (tenant_id, created_at),
    INDEX ix_bills_tenant_status (tenant_id, status),
    INDEX ix_bills_tenant_status_created_at (tenant_id, status, created_at),
    INDEX ix_bills_tenant_created_by (tenant_id, created_by),
    INDEX ix_bills_tenant_payment_method (tenant_id, payment_method),
    CONSTRAINT fk_bills_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bills_created_by
        FOREIGN KEY (created_by) REFERENCES users (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bills_cancelled_by
        FOREIGN KEY (cancelled_by) REFERENCES users (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_bills_status CHECK (status IN ('DRAFT', 'FINALIZED', 'CANCELLED', 'VOID')),
    CONSTRAINT chk_bills_payment_method CHECK (payment_method IN ('cash', 'online')),
    CONSTRAINT chk_bills_money CHECK (
        subtotal >= 0 AND discount >= 0 AND taxable_amount >= 0
        AND cgst_amount >= 0 AND sgst_amount >= 0 AND gst_amount >= 0
        AND grand_total >= 0 AND printed_count >= 0
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- bill_items (price/GST/name snapshots for historical accuracy)
-- -----------------------------------------------------------------------------
CREATE TABLE bill_items (
    id               CHAR(36)       NOT NULL,
    tenant_id        CHAR(36)       NOT NULL,
    bill_id          CHAR(36)       NOT NULL,
    item_id          CHAR(36)       NULL,
    item_name        VARCHAR(200)   NOT NULL,
    quantity         DECIMAL(10,3)  NOT NULL,
    unit_price       DECIMAL(12,2)  NOT NULL,
    gst_percentage   DECIMAL(5,2)   NOT NULL DEFAULT 0.00,
    discount         DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    taxable_amount   DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    cgst_amount      DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    sgst_amount      DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    total            DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    created_at       DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_bill_items_tenant_bill (tenant_id, bill_id),
    INDEX ix_bill_items_tenant_item (tenant_id, item_id),
    CONSTRAINT fk_bill_items_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bill_items_bill
        FOREIGN KEY (bill_id) REFERENCES bills (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bill_items_item
        FOREIGN KEY (item_id) REFERENCES items (id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_bill_items_qty CHECK (quantity > 0),
    CONSTRAINT chk_bill_items_money CHECK (
        unit_price >= 0 AND discount >= 0 AND taxable_amount >= 0
        AND cgst_amount >= 0 AND sgst_amount >= 0 AND total >= 0
        AND gst_percentage >= 0 AND gst_percentage <= 100
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- notifications (tenant-scoped in-app alerts)
-- -----------------------------------------------------------------------------
CREATE TABLE notifications (
    id            CHAR(36)     NOT NULL,
    tenant_id     CHAR(36)     NOT NULL,
    user_id       CHAR(36)     NULL,
    type          VARCHAR(50)  NOT NULL,
    title         VARCHAR(160) NOT NULL,
    message       TEXT         NOT NULL,
    entity_type   VARCHAR(50)  NULL,
    entity_id     CHAR(36)     NULL,
    is_read       BOOLEAN      NOT NULL DEFAULT FALSE,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- tenant_whatsapp_configs (per-tenant WhatsApp Cloud API credentials)
-- -----------------------------------------------------------------------------
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- bill_deliveries (WhatsApp / delivery attempts — not financial status)
-- -----------------------------------------------------------------------------
CREATE TABLE bill_deliveries (
    id                        CHAR(36)     NOT NULL,
    tenant_id                 CHAR(36)     NOT NULL,
    bill_id                   CHAR(36)     NOT NULL,
    delivery_method           VARCHAR(20)  NOT NULL,
    recipient_phone_e164      VARCHAR(20)  NULL,
    recipient_phone_masked    VARCHAR(32)  NULL,
    recipient_email           VARCHAR(255) NULL,
    recipient_email_masked    VARCHAR(64)  NULL,
    status                    VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    provider_message_id       VARCHAR(120) NULL,
    error_message             TEXT         NULL,
    attempted_by              CHAR(36)     NULL,
    sent_at                   DATETIME(6)  NULL,
    delivered_at              DATETIME(6)  NULL,
    read_at                   DATETIME(6)  NULL,
    created_at                DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at                DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                         ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_bill_deliveries_tenant_bill (tenant_id, bill_id),
    INDEX ix_bill_deliveries_tenant_created (tenant_id, created_at),
    INDEX ix_bill_deliveries_tenant_method_bill_created
        (tenant_id, delivery_method, bill_id, created_at),
    INDEX ix_bill_deliveries_provider_message (provider_message_id),
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
        CHECK (delivery_method IN ('WHATSAPP', 'PRINT', 'EMAIL')),
    CONSTRAINT chk_bill_deliveries_status
        CHECK (status IN ('PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- audit_logs (append-only from application perspective)
-- -----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id            CHAR(36)     NOT NULL,
    tenant_id     CHAR(36)     NOT NULL,
    user_id       CHAR(36)     NULL,
    user_name     VARCHAR(120) NULL,
    action        VARCHAR(50)  NOT NULL,
    entity_type   VARCHAR(50)  NOT NULL,
    entity_id     CHAR(36)     NULL,
    old_data      JSON         NULL,
    new_data      JSON         NULL,
    ip_address    VARCHAR(45)  NULL,
    user_agent    VARCHAR(255) NULL,
    created_at    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_audit_logs_tenant_created_at (tenant_id, created_at),
    INDEX ix_audit_logs_tenant_user (tenant_id, user_id),
    INDEX ix_audit_logs_tenant_action (tenant_id, action),
    INDEX ix_audit_logs_tenant_entity (tenant_id, entity_type, entity_id),
    CONSTRAINT fk_audit_logs_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- stock_movements (inventory quantity ledger)
-- -----------------------------------------------------------------------------
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
    INDEX ix_stock_movements_tenant_item_created (tenant_id, item_id, created_at),
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Seed: roles (exactly two)
-- -----------------------------------------------------------------------------
INSERT INTO roles (id, name, description) VALUES
    ('11111111-1111-1111-1111-111111111111', 'OWNER', 'Business owner with full tenant management access'),
    ('22222222-2222-2222-2222-222222222222', 'BILLING_USER', 'Counter billing user with limited access');

-- Done
SELECT 'business billing schema created successfully' AS message;
SHOW TABLES;
