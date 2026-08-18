"""Master Admin data access — platform scoped (no tenant_id)."""

from sqlalchemy import func

from app.extensions import db
from app.models.master_admin import MasterAdmin


class MasterAdminRepository:
    @staticmethod
    def get_by_id(admin_id: str) -> MasterAdmin | None:
        return db.session.get(MasterAdmin, admin_id)

    @staticmethod
    def find_by_email(email: str) -> MasterAdmin | None:
        if not email:
            return None
        return (
            db.session.query(MasterAdmin)
            .filter(func.lower(MasterAdmin.email) == email.lower().strip())
            .first()
        )

    @staticmethod
    def add(row: MasterAdmin) -> MasterAdmin:
        db.session.add(row)
        return row
