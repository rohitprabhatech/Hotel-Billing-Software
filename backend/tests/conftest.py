"""Pytest fixtures for auth and tenant isolation tests."""

import pytest

from app import create_app
from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER, Role
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.security import hash_password


@pytest.fixture()
def app():
    application = create_app("testing")
    application.config["JWT_SECRET_KEY"] = "test-jwt-secret-key-32chars-min!!"
    application.config["SECRET_KEY"] = "test-secret-key-32chars-minimum!!"

    with application.app_context():
        db.create_all()
        _seed(db.session)
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed(session):
    owner_role = Role(
        id="11111111-1111-1111-1111-111111111111",
        name=ROLE_OWNER,
        description="Owner",
    )
    billing_role = Role(
        id="22222222-2222-2222-2222-222222222222",
        name=ROLE_BILLING_USER,
        description="Billing",
    )
    tenant_a = Tenant(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        name="Hotel A",
        business_name="Hotel A",
        status="ACTIVE",
    )
    tenant_b = Tenant(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        name="Hotel B",
        business_name="Hotel B",
        status="ACTIVE",
    )
    users = [
        User(
            id="a1111111-1111-1111-1111-111111111111",
            tenant_id=tenant_a.id,
            role_id=owner_role.id,
            name="Owner A",
            email="owner@hotela.com",
            password_hash=hash_password("Owner@12345"),
            is_active=True,
        ),
        User(
            id="a2222222-2222-2222-2222-222222222222",
            tenant_id=tenant_a.id,
            role_id=billing_role.id,
            name="Billing A",
            email="billing@hotela.com",
            password_hash=hash_password("Billing@12345"),
            is_active=True,
        ),
        User(
            id="b1111111-1111-1111-1111-111111111111",
            tenant_id=tenant_b.id,
            role_id=owner_role.id,
            name="Owner B",
            email="owner@hotelb.com",
            password_hash=hash_password("Owner@12345"),
            is_active=True,
        ),
    ]
    session.add_all([owner_role, billing_role, tenant_a, tenant_b, *users])
    session.commit()


def login(client, email, password):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.get_json()
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
