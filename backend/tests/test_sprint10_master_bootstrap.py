"""Sprint 10: first Master Admin seed is idempotent and validates input."""

from app.models.master_admin import MasterAdmin
from app.services.master_bootstrap_service import MasterBootstrapService
from app.utils.exceptions import ValidationError
from tests.conftest import login


def test_seed_rejects_missing_email(app):
    with app.app_context():
        try:
            MasterBootstrapService.seed_first(email="", password="Master@12345", name="Ops")
            assert False, "expected ValidationError"
        except ValidationError as exc:
            assert "MASTER_ADMIN_EMAIL" in str(exc)


def test_seed_rejects_short_password(app):
    with app.app_context():
        try:
            MasterBootstrapService.seed_first(email="ops@prabhatech.test", password="short", name="Ops")
            assert False, "expected ValidationError"
        except ValidationError as exc:
            assert "MASTER_ADMIN_PASSWORD" in str(exc)


def test_seed_creates_once_and_logs_in(client, app):
    with app.app_context():
        assert MasterBootstrapService.seed_first(
            email="ops-bootstrap@prabhatech.test",
            password="Master@12345",
            name="Ops Bootstrap",
        ) == "created"
        assert MasterBootstrapService.seed_first(
            email="ops-bootstrap@prabhatech.test",
            password="Master@12345",
            name="Ops Bootstrap",
        ) == "exists"
        assert MasterAdmin.query.filter_by(email="ops-bootstrap@prabhatech.test").count() == 1

    headers = login(client, "ops-bootstrap@prabhatech.test", "Master@12345")
    summary = client.get("/api/v1/master/dashboard/summary", headers=headers)
    assert summary.status_code == 200, summary.get_json()


def test_seed_rejects_business_user_email(app):
    with app.app_context():
        try:
            MasterBootstrapService.seed_first(
                email="owner@hotela.com",
                password="Master@12345",
                name="Clash",
            )
            assert False, "expected ValidationError"
        except ValidationError as exc:
            assert "business user" in str(exc).lower()
