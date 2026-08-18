"""Create the first Master Admin from environment variables (idempotent).

Does not overwrite an existing row. Never commit real passwords to source.

  MASTER_ADMIN_EMAIL
  MASTER_ADMIN_PASSWORD   (min 8 characters)
  MASTER_ADMIN_NAME       (optional, default: Prabha Technology Admin)
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.master_admin import MasterAdmin  # noqa: E402
from app.repositories.master_admin_repository import MasterAdminRepository  # noqa: E402
from app.repositories.user_repository import UserRepository  # noqa: E402
from app.utils.ids import new_uuid  # noqa: E402
from app.utils.security import hash_password  # noqa: E402


def main() -> int:
    email = (os.environ.get("MASTER_ADMIN_EMAIL") or "").strip().lower()
    password = os.environ.get("MASTER_ADMIN_PASSWORD") or ""
    name = (os.environ.get("MASTER_ADMIN_NAME") or "Prabha Technology Admin").strip()

    if not email or "@" not in email:
        print("MASTER_ADMIN_EMAIL is required", file=sys.stderr)
        return 1
    if len(password) < 8:
        print("MASTER_ADMIN_PASSWORD must be at least 8 characters", file=sys.stderr)
        return 1

    app = create_app()
    with app.app_context():
        if MasterAdminRepository.find_by_email(email):
            print(f"Master admin already exists: {email}")
            return 0
        if UserRepository.find_by_email(email):
            print("That email is already a business user. Choose another.", file=sys.stderr)
            return 1
        admin = MasterAdmin(
            id=new_uuid(),
            name=name,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            token_version=0,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Created master admin: {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
