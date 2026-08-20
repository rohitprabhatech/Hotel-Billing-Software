"""Sprint 8: DATABASE_URL or MYSQL_* connection resolution."""

import os

import pytest

from app.utils.database_url import require_database_url, resolve_database_url


def test_resolve_prefers_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://a:b@host:3306/live_db")
    monkeypatch.setenv("MYSQL_HOST", "ignored.example")
    monkeypatch.setenv("MYSQL_USER", "ignored")
    monkeypatch.setenv("MYSQL_DATABASE", "ignored")
    assert resolve_database_url() == "mysql+pymysql://a:b@host:3306/live_db"


def test_resolve_builds_url_from_mysql_parts(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MYSQL_HOST", "sql.example.com")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_USER", "shop_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "p@ss:word/1")
    monkeypatch.setenv("MYSQL_DATABASE", "u583892242_HotelBillingDB")
    url = resolve_database_url()
    assert url is not None
    assert url.startswith("mysql+pymysql://shop_user:")
    assert "@sql.example.com:3307/u583892242_HotelBillingDB" in url
    assert "p@ss" not in url
    assert "p%40ss" in url


def test_resolve_none_when_incomplete(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.delenv("MYSQL_USER", raising=False)
    monkeypatch.delenv("MYSQL_DATABASE", raising=False)
    assert resolve_database_url() is None
    with pytest.raises(RuntimeError, match="MYSQL_HOST"):
        require_database_url()


def test_testing_config_stays_sqlite():
    from app.config.settings import TestingConfig

    assert TestingConfig.SQLALCHEMY_DATABASE_URI.startswith("sqlite:")
