"""Pytest fixtures for auth and tenant isolation tests."""

import pytest

from app import create_app
from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER, Role
from app.models.subscription import PAYMENT_COMPLIMENTARY, SUBSCRIPTION_ACTIVE, Subscription
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.ids import new_uuid
from app.utils.security import hash_password
from app.utils.tokens import utc_now_naive


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
    manager_role = Role(
        id="33333333-3333-3333-3333-333333333333",
        name=ROLE_MANAGER,
        description="Manager",
    )
    tenant_a = Tenant(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        name="Hotel A",
        business_name="Hotel A",
        business_type="hotel_restaurant",
        status="ACTIVE",
    )
    tenant_b = Tenant(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        name="Hotel B",
        business_name="Hotel B",
        business_type="cafe_tea",
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
            email_verified=True,
            token_version=0,
        ),
        User(
            id="a2222222-2222-2222-2222-222222222222",
            tenant_id=tenant_a.id,
            role_id=billing_role.id,
            name="Billing A",
            email="billing@hotela.com",
            password_hash=hash_password("Billing@12345"),
            is_active=True,
            email_verified=True,
            token_version=0,
        ),
        User(
            id="a3333333-3333-3333-3333-333333333333",
            tenant_id=tenant_a.id,
            role_id=manager_role.id,
            name="Manager A",
            email="manager@hotela.com",
            password_hash=hash_password("Manager@12345"),
            is_active=True,
            email_verified=True,
            token_version=0,
        ),
        User(
            id="b1111111-1111-1111-1111-111111111111",
            tenant_id=tenant_b.id,
            role_id=owner_role.id,
            name="Owner B",
            email="owner@hotelb.com",
            password_hash=hash_password("Owner@12345"),
            is_active=True,
            email_verified=True,
            token_version=0,
        ),
    ]
    session.add_all([owner_role, billing_role, manager_role, tenant_a, tenant_b, *users])
    now = utc_now_naive()
    session.add_all(
        [
            Subscription(
                id=new_uuid(),
                tenant_id=tenant_a.id,
                status=SUBSCRIPTION_ACTIVE,
                starts_at=now,
                ends_at=None,
                payment_status=PAYMENT_COMPLIMENTARY,
            ),
            Subscription(
                id=new_uuid(),
                tenant_id=tenant_b.id,
                status=SUBSCRIPTION_ACTIVE,
                starts_at=now,
                ends_at=None,
                payment_status=PAYMENT_COMPLIMENTARY,
            ),
        ]
    )
    session.commit()


def login(client, email, password):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.get_json()
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_master_admin(
    app,
    *,
    email="master@prabhatech.test",
    password="Master@12345",
    active=True,
):
    from app.models.master_admin import MasterAdmin
    from app.repositories.master_admin_repository import MasterAdminRepository
    from app.utils.ids import new_uuid

    with app.app_context():
        existing = MasterAdminRepository.find_by_email(email)
        if existing is not None:
            return email
        admin = MasterAdmin(
            id=new_uuid(),
            name="Prabha Technology Admin",
            email=email,
            password_hash=hash_password(password),
            is_active=active,
            token_version=0,
        )
        db.session.add(admin)
        db.session.commit()
    return email


def login_master(client, app, *, email="master@prabhatech.test", password="Master@12345"):
    seed_master_admin(app, email=email, password=password)
    return login(client, email, password)
