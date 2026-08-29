"""Cafe billing hardening — timezone typo must not 500 billing home APIs."""

from tests.conftest import login


def test_today_summary_tolerates_report_timezone_typo(client, app):
    """Asia/Kolkatar env typo previously crashed /bills/today-summary with ZoneInfoNotFoundError."""
    app.config["REPORT_TIMEZONE"] = "Asia/Kolkatar"
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/bills/today-summary", headers=headers)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()["data"]
    assert "total_sales" in body
    assert "bill_count" in body


def test_cafe_dashboard_tolerates_report_timezone_typo(client, app):
    app.config["REPORT_TIMEZONE"] = "Asia/Kolkatar"
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/cafe/dashboard?period=today", headers=headers)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()["data"]
    assert body["period"] == "today"
    assert "current" in body
