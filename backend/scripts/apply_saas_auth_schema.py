"""Apply SaaS auth columns/tables to the current DATABASE_URL if missing."""

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db


def main():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())
        user_cols = {c["name"] for c in inspector.get_columns("users")} if "users" in tables else set()

        if "email_verified" not in user_cols:
            print("Adding users auth columns...")
            db.session.execute(text(
                "ALTER TABLE users "
                "ADD COLUMN email_verified TINYINT(1) NOT NULL DEFAULT 0, "
                "ADD COLUMN email_verified_at DATETIME(6) NULL, "
                "ADD COLUMN password_changed_at DATETIME(6) NULL, "
                "ADD COLUMN pending_email VARCHAR(255) NULL, "
                "ADD COLUMN token_version INT NOT NULL DEFAULT 0"
            ))
            db.session.execute(text("UPDATE users SET email_verified = 1"))
            db.session.commit()
            print("users columns added; existing users marked verified")
        else:
            print("users auth columns already present")

        if "password_reset_tokens" not in tables:
            print("Creating password_reset_tokens...")
            db.session.execute(text(
                """
                CREATE TABLE password_reset_tokens (
                    id CHAR(36) NOT NULL,
                    user_id CHAR(36) NOT NULL,
                    token_hash CHAR(64) NOT NULL,
                    expires_at DATETIME(6) NOT NULL,
                    used_at DATETIME(6) NULL,
                    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    UNIQUE KEY uq_password_reset_token_hash (token_hash),
                    INDEX ix_password_reset_user_id (user_id),
                    CONSTRAINT fk_password_reset_user
                        FOREIGN KEY (user_id) REFERENCES users (id)
                        ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            ))
            db.session.commit()
        else:
            print("password_reset_tokens already present")

        if "email_verification_tokens" not in tables:
            print("Creating email_verification_tokens...")
            db.session.execute(text(
                """
                CREATE TABLE email_verification_tokens (
                    id CHAR(36) NOT NULL,
                    user_id CHAR(36) NOT NULL,
                    token_hash CHAR(64) NOT NULL,
                    purpose VARCHAR(40) NOT NULL DEFAULT 'signup',
                    new_email VARCHAR(255) NULL,
                    expires_at DATETIME(6) NOT NULL,
                    verified_at DATETIME(6) NULL,
                    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                    PRIMARY KEY (id),
                    UNIQUE KEY uq_email_verification_token_hash (token_hash),
                    INDEX ix_email_verification_user_id (user_id),
                    CONSTRAINT fk_email_verification_user
                        FOREIGN KEY (user_id) REFERENCES users (id)
                        ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            ))
            db.session.commit()
        else:
            print("email_verification_tokens already present")

        print("Done.")


if __name__ == "__main__":
    main()
