"""Resolve MySQL URL from DATABASE_URL or split MYSQL_* env vars."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


def load_backend_env() -> None:
    """Load backend/.env without overriding already-set process env."""
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")


def resolve_database_url() -> str | None:
    """Return a SQLAlchemy URL, or None if neither DATABASE_URL nor MYSQL_* is complete.

    DATABASE_URL wins when set. Otherwise:
    MYSQL_HOST, MYSQL_USER, MYSQL_DATABASE, optional MYSQL_PASSWORD / MYSQL_PORT.
    """
    direct = (os.getenv("DATABASE_URL") or "").strip()
    if direct:
        return direct

    host = (os.getenv("MYSQL_HOST") or "").strip()
    user = (os.getenv("MYSQL_USER") or "").strip()
    database = (os.getenv("MYSQL_DATABASE") or "").strip()
    if not host or not user or not database:
        return None

    password = os.getenv("MYSQL_PASSWORD") or ""
    port = (os.getenv("MYSQL_PORT") or "3306").strip() or "3306"
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{database}"
    )


def require_database_url() -> str:
    url = resolve_database_url()
    if not url:
        raise RuntimeError(
            "Set DATABASE_URL, or MYSQL_HOST + MYSQL_USER + MYSQL_DATABASE "
            "(optional MYSQL_PASSWORD, MYSQL_PORT)."
        )
    return url
