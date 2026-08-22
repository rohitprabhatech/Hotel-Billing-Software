"""
Controlled onboarding for a new business tenant + owner user.

Usage (from backend/ with venv active):
  python scripts/onboard_tenant.py ^
    --business-name "Sunrise Cafe" ^
    --name "Sunrise Cafe" ^
    --business-type restaurant ^
    --owner-name "Ramesh" ^
    --owner-email "owner@sunrisecafe.com" ^
    --owner-password "ChangeMe@12345" ^
    --phone "9000000000" ^
    --city "Pune"

Optional billing user:
  --billing-name "Counter 1" --billing-email "billing@sunrisecafe.com" --billing-password "ChangeMe@12345"
"""

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.constants.business_types import DEFAULT_BUSINESS_TYPE, normalize_business_type
from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER, Role
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.ids import new_uuid
from app.utils.security import hash_password

ROLE_OWNER_ID = "11111111-1111-1111-1111-111111111111"
ROLE_BILLING_ID = "22222222-2222-2222-2222-222222222222"
ROLE_MANAGER_ID = "33333333-3333-3333-3333-333333333333"


def ensure_roles():
    for role_id, name, description in [
        (ROLE_OWNER_ID, ROLE_OWNER, "Business owner with full tenant management access"),
        (ROLE_BILLING_ID, ROLE_BILLING_USER, "Counter billing user with limited access"),
        (ROLE_MANAGER_ID, ROLE_MANAGER, "Operations manager — billing, reports, stock"),
    ]:
        role = db.session.get(Role, role_id) or Role.query.filter_by(name=name).first()
        if role is None:
            db.session.add(Role(id=role_id, name=name, description=description))


def main():
    parser = argparse.ArgumentParser(description="Onboard a business tenant")
    parser.add_argument("--business-name", required=True)
    parser.add_argument("--name", required=True, help="Business display name")
    parser.add_argument(
        "--business-type",
        default=DEFAULT_BUSINESS_TYPE,
        help="Business type code (restaurant, hotel, clothing_store, ...)",
    )
    parser.add_argument("--owner-name", required=True)
    parser.add_argument("--owner-email", required=True)
    parser.add_argument("--owner-password", required=True)
    parser.add_argument("--phone", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--address", default=None)
    parser.add_argument("--city", default=None)
    parser.add_argument("--state", default=None)
    parser.add_argument("--pincode", default=None)
    parser.add_argument("--gst-number", default=None)
    parser.add_argument("--fssai-number", default=None)
    parser.add_argument("--bill-prefix", default=None)
    parser.add_argument("--billing-name", default=None)
    parser.add_argument("--billing-email", default=None)
    parser.add_argument("--billing-password", default=None)
    args = parser.parse_args()

    if len(args.owner_password) < 8:
        raise SystemExit("Owner password must be at least 8 characters")

    try:
        business_type = normalize_business_type(args.business_type)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    app = create_app()
    with app.app_context():
        ensure_roles()
        owner_role = Role.query.filter_by(name=ROLE_OWNER).first()
        billing_role = Role.query.filter_by(name=ROLE_BILLING_USER).first()

        tenant = Tenant(
            id=new_uuid(),
            name=args.name.strip(),
            business_name=args.business_name.strip(),
            business_type=business_type,
            address=args.address,
            city=args.city,
            state=args.state,
            pincode=args.pincode,
            phone=args.phone,
            email=args.email,
            gst_number=args.gst_number,
            fssai_number=args.fssai_number,
            bill_number_prefix=args.bill_prefix,
            status="ACTIVE",
        )
        db.session.add(tenant)
        db.session.flush()

        owner = User(
            id=new_uuid(),
            tenant_id=tenant.id,
            role_id=owner_role.id,
            name=args.owner_name.strip(),
            email=args.owner_email.strip().lower(),
            password_hash=hash_password(args.owner_password),
            is_active=True,
            email_verified=True,
            token_version=0,
        )
        db.session.add(owner)

        if args.billing_email:
            if not args.billing_name or not args.billing_password:
                raise SystemExit("Billing user requires --billing-name and --billing-password")
            if len(args.billing_password) < 8:
                raise SystemExit("Billing password must be at least 8 characters")
            db.session.add(
                User(
                    id=new_uuid(),
                    tenant_id=tenant.id,
                    role_id=billing_role.id,
                    name=args.billing_name.strip(),
                    email=args.billing_email.strip().lower(),
                    password_hash=hash_password(args.billing_password),
                    is_active=True,
                    email_verified=True,
                    token_version=0,
                )
            )

        db.session.commit()
        print(f"Onboarded tenant {tenant.id} ({tenant.business_name}) type={tenant.business_type}")
        print(f"Owner: {owner.email}")


if __name__ == "__main__":
    main()
