"""Environment-based application configuration."""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/hotel_billing",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    CORS_ORIGINS = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    REPORT_TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Kolkata")

    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    env = name or os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)