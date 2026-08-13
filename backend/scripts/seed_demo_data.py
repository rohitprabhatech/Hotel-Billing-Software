"""
Seed demo tenants and users for local development.

Usage (from backend/):
  .\\.venv\\Scripts\\python scripts\\seed_demo_data.py
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER, Role
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.ids import new_uuid
from app.utils.security import hash_password

ROLE_OWNER_ID = "11111111-1111-1111-1111-111111111111"
ROLE_BILLING_ID = "22222222-2222-2222-2222-222222222222"

TENANT_A_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TENANT_B_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def upsert_role(role_id: str, name: str, description: str):
    role = db.session.get(Role, role_id) or Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(id=role_id, name=name, description=description)
        db.session.add(role)
    else:
        role.name = name
        role.description = description
    return role


def upsert_tenant(tenant_id: str, **kwargs):
    tenant = db.session.get(Tenant, tenant_id)
    if tenant is None:
        tenant = Tenant(id=tenant_id, **kwargs)
        db.session.add(tenant)
    else:
        for key, value in kwargs.items():
            setattr(tenant, key, value)
    return tenant


def upsert_user(*, user_id: str, tenant_id: str, role_id: str, name: str, email: str, password: str):
    user = db.session.get(User, user_id)
    if user is None:
        existing = User.query.filter_by(tenant_id=tenant_id, email=email.lower()).first()
        if existing:
            user = existing
        else:
            user = User(id=user_id, tenant_id=tenant_id, role_id=role_id, email=email.lower())
            db.session.add(user)
    user.tenant_id = tenant_id
    user.role_id = role_id
    user.name = name
    user.email = email.lower()
    user.password_hash = hash_password(password)
    user.is_active = True
    user.email_verified = True
    user.token_version = int(getattr(user, "token_version", 0) or 0)
    return user


def main():
    app = create_app()
    with app.app_context():
        upsert_role(ROLE_OWNER_ID, ROLE_OWNER, "Hotel owner with full tenant management access")
        upsert_role(
            ROLE_BILLING_ID,
            ROLE_BILLING_USER,
            "Counter billing user with limited access",
        )

        upsert_tenant(
            TENANT_A_ID,
            name="Hotel A",
            business_name="Hotel A Family Restaurant",
            address="MG Road",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            phone="9000000001",
            email="hotel.a@example.com",
            gst_number="27AAAAA0000A1Z5",
            fssai_number="10000000000001",
            bill_number_prefix="INV-A-",
            status="ACTIVE",
        )
        upsert_tenant(
            TENANT_B_ID,
            name="Hotel B",
            business_name="Hotel B Pure Veg",
            address="FC Road",
            city="Pune",
            state="Maharashtra",
            pincode="411004",
            phone="9000000002",
            email="hotel.b@example.com",
            gst_number="27BBBBB0000B1Z5",
            fssai_number="10000000000002",
            bill_number_prefix="INV-B-",
            status="ACTIVE",
        )

        upsert_user(
            user_id="a1111111-1111-1111-1111-111111111111",
            tenant_id=TENANT_A_ID,
            role_id=ROLE_OWNER_ID,
            name="Owner A",
            email="owner@hotela.com",
            password="Owner@12345",
        )
        upsert_user(
            user_id="a2222222-2222-2222-2222-222222222222",
            tenant_id=TENANT_A_ID,
            role_id=ROLE_BILLING_ID,
            name="Billing User A",
            email="billing@hotela.com",
            password="Billing@12345",
        )
        upsert_user(
            user_id="b1111111-1111-1111-1111-111111111111",
            tenant_id=TENANT_B_ID,
            role_id=ROLE_OWNER_ID,
            name="Owner B",
            email="owner@hotelb.com",
            password="Owner@12345",
        )
        upsert_user(
            user_id="b2222222-2222-2222-2222-222222222222",
            tenant_id=TENANT_B_ID,
            role_id=ROLE_BILLING_ID,
            name="Billing User B",
            email="billing@hotelb.com",
            password="Billing@12345",
        )

        db.session.commit()
        print("Demo data seeded successfully.")
        print("Hotel A Owner : owner@hotela.com / Owner@12345")
        print("Hotel A Billing: billing@hotela.com / Billing@12345")
        print("Hotel B Owner : owner@hotelb.com / Owner@12345")
        print("Hotel B Billing: billing@hotelb.com / Billing@12345")


if __name__ == "__main__":
    main()