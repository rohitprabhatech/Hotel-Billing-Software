"""Create the first Master Admin (idempotent). Does not overwrite passwords."""

from app.models.master_admin import MasterAdmin
from app.repositories.master_admin_repository import MasterAdminRepository
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ValidationError
from app.utils.ids import new_uuid
from app.utils.security import hash_password


class MasterBootstrapService:
    @staticmethod
    def seed_first(*, email: str, password: str, name: str) -> str:
        """Insert one Master Admin. Returns 'created' or 'exists'."""
        cleaned = (email or "").strip().lower()
        label = (name or "Prabha Technology Admin").strip() or "Prabha Technology Admin"
        if not cleaned or "@" not in cleaned:
            raise ValidationError("MASTER_ADMIN_EMAIL is required")
        if len(password or "") < 8:
            raise ValidationError("MASTER_ADMIN_PASSWORD must be at least 8 characters")

        existing = MasterAdminRepository.find_by_email(cleaned)
        if existing is not None:
            return "exists"
        if UserRepository.find_by_email(cleaned):
            raise ValidationError("That email is already a business user. Choose another.")

        MasterAdminRepository.add(
            MasterAdmin(
                id=new_uuid(),
                name=label,
                email=cleaned,
                password_hash=hash_password(password),
                is_active=True,
                token_version=0,
            )
        )
        from app.extensions import db

        db.session.commit()
        return "created"
