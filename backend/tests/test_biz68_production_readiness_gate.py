"""Sprint BIZ-68 — production readiness gate (industry go-live dry-run)."""

from pathlib import Path

from tests.conftest import login

BACKEND = Path(__file__).resolve().parents[1]
DOCS_SPRINTS = BACKEND.parent / "docs" / "14-sprints"
CHECKLIST = DOCS_SPRINTS / "biz-68-industry-go-live-checklist.md"
REPORT = DOCS_SPRINTS / "biz-68-production-readiness-gate-report.md"


def test_go_live_checklist_covers_required_topics():
    assert CHECKLIST.is_file()
    text = CHECKLIST.read_text(encoding="utf-8")
    for needle in (
        "Medical",
        "excluded",
        "02_schema.sql",
        "/api/v1/health",
        "health/ready",
        "backup",
        "check_platform_ready.py",
        "backup_database.py",
        "BIZ-64",
        "business_type",
        "Travel agencies",
        "Wholesale",
    ):
        assert needle in text, needle


def test_gate_report_and_support_scripts_exist():
    assert REPORT.is_file()
    report = REPORT.read_text(encoding="utf-8")
    assert "PASSED" in report or "APPROVED" in report
    assert "Medical" in report

    scripts = BACKEND / "scripts"
    for name in (
        "check_platform_ready.py",
        "backup_database.py",
        "print_alembic_chain.py",
        "stamp_alembic_industry_head.py",
        "onboard_tenant.py",
        "inspect_database_schema.py",
    ):
        assert (scripts / name).is_file(), name

    runbook = BACKEND.parent / "docs" / "03-database" / "10-industry-modules-ops-runbook.md"
    assert runbook.is_file()


def test_health_liveness_and_readiness(client):
    live = client.get("/api/v1/health")
    assert live.status_code == 200
    assert live.get_json()["data"]["status"] == "ok"

    ready = client.get("/api/v1/health/ready")
    assert ready.status_code == 200
    data = ready.get_json()["data"]
    assert data["status"] == "ready"
    assert data["database"] == "ok"


def test_owner_can_reach_notifications_after_login(client):
    """Smoke: authenticated envelope still works post industry packs."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    notes = client.get("/api/v1/notifications/unread-count", headers=owner)
    assert notes.status_code == 200
    assert notes.get_json()["success"] is True
