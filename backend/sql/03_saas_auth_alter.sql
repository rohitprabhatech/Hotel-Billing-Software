-- Historical incremental alter for the SaaS-auth release (MySQL).
--
-- This file intentionally covers only the authentication changes introduced in
-- that release. It is NOT a complete upgrade for the current application.
-- For an existing database, use backend/scripts/apply_pending_schema.py.
-- For a fresh database, use 01_create_database.sql followed by 02_schema.sql.

USE hotel_billing;

ALTER TABLE users
    ADD COLUMN email_verified TINYINT(1) NOT NULL DEFAULT 0 AFTER is_active,
    ADD COLUMN email_verified_at DATETIME(6) NULL AFTER email_verified,
    ADD COLUMN password_changed_at DATETIME(6) NULL AFTER email_verified_at,
    ADD COLUMN pending_email VARCHAR(255) NULL AFTER password_changed_at,
    ADD COLUMN token_version INT NOT NULL DEFAULT 0 AFTER pending_email;

UPDATE users SET email_verified = 1 WHERE email_verified = 0;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
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

CREATE TABLE IF NOT EXISTS email_verification_tokens (
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
