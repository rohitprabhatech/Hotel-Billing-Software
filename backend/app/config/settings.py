"""Environment-based application configuration."""

import os
import tempfile
from datetime import timedelta

from dotenv import load_dotenv

from app.utils.database_url import resolve_database_url

load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "28800"))
    )

    SQLALCHEMY_DATABASE_URI = resolve_database_url() or (
        "mysql+pymysql://root:password@localhost/hotel_billing?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "280")),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_POOL_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "connect_args": {"charset": "utf8mb4"},
    }

    CORS_ORIGINS = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    REPORT_TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Kolkata")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    # Email / SMTP (provider-agnostic)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in {"1", "true", "yes"}
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in {"1", "true", "yes"}
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@businessbilling.local")
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    EMAIL_VERIFICATION_REQUIRED = os.getenv(
        "EMAIL_VERIFICATION_REQUIRED", "true"
    ).lower() in {"1", "true", "yes"}
    SEND_LOGIN_NOTIFICATIONS = os.getenv(
        "SEND_LOGIN_NOTIFICATIONS", "false"
    ).lower() in {"1", "true", "yes"}
    # Expose raw tokens in API responses for local/testing only
    ALLOW_DEV_AUTH_TOKENS = os.getenv("ALLOW_DEV_AUTH_TOKENS", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    # WhatsApp Cloud API
    WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "mock").lower()  # mock | meta
    WHATSAPP_TOKEN_ENCRYPTION_KEY = os.getenv("WHATSAPP_TOKEN_ENCRYPTION_KEY", "")
    WHATSAPP_GRAPH_API_VERSION = os.getenv("WHATSAPP_GRAPH_API_VERSION", "v21.0")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")

    TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(3 * 1024 * 1024)))
    MAX_ITEM_IMAGE_BYTES = int(os.getenv("MAX_ITEM_IMAGE_BYTES", str(2 * 1024 * 1024)))
    ITEM_IMAGE_UPLOAD_DIR = os.getenv(
        "ITEM_IMAGE_UPLOAD_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "item-images"),
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    ALLOW_DEV_AUTH_TOKENS = os.getenv("ALLOW_DEV_AUTH_TOKENS", "true").lower() in {
        "1",
        "true",
        "yes",
    }


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}
    MAIL_SUPPRESS_SEND = True
    EMAIL_VERIFICATION_REQUIRED = True
    ALLOW_DEV_AUTH_TOKENS = True
    SEND_LOGIN_NOTIFICATIONS = False
    FRONTEND_URL = "http://localhost:5173"
    WHATSAPP_PROVIDER = "mock"
    WHATSAPP_TOKEN_ENCRYPTION_KEY = "test-whatsapp-encryption-key-32b!"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = "test-verify-token"
    WHATSAPP_APP_SECRET = "test-app-secret"
    ITEM_IMAGE_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "hbs-test-item-images")


class ProductionConfig(BaseConfig):
    DEBUG = False
    ALLOW_DEV_AUTH_TOKENS = False

    @classmethod
    def validate(cls):
        weak_secrets = {
            "dev-only-secret-change-me",
            "change-me-to-a-long-random-secret",
            "change-me-to-another-long-random-secret",
            "dev-only-jwt-secret-change-me",
        }
        if not cls.SECRET_KEY or cls.SECRET_KEY in weak_secrets or len(cls.SECRET_KEY) < 32:
            raise RuntimeError("Production SECRET_KEY must be a strong value (32+ chars)")
        if (
            not cls.JWT_SECRET_KEY
            or cls.JWT_SECRET_KEY in weak_secrets
            or len(cls.JWT_SECRET_KEY) < 32
        ):
            raise RuntimeError("Production JWT_SECRET_KEY must be a strong value (32+ chars)")
        if "password@" in (cls.SQLALCHEMY_DATABASE_URI or ""):
            raise RuntimeError("Production DATABASE_URL still looks like a placeholder")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    env = name or os.getenv("FLASK_ENV", "development")
    config = config_by_name.get(env, DevelopmentConfig)
    if env == "production" and hasattr(config, "validate"):
        config.validate()
    return config