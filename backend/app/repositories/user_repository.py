"""User data access — always tenant-aware for mutating/list operations."""

from sqlalchemy import func

from app.extensions import db
from app.models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_id_and_tenant(user_id: str, tenant_id: str) -> User | None:
        return (
            db.session.query(User)
            .filter(User.id == user_id, User.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def find_by_email(email: str) -> list[User]:
        return (
            db.session.query(User)
            .filter(func.lower(User.email) == email.lower().strip())
            .all()
        )

    @staticmethod
    def find_by_tenant_and_email(tenant_id: str, email: str) -> User | None:
        return (
            db.session.query(User)
            .filter(
                User.tenant_id == tenant_id,
                func.lower(User.email) == email.lower().strip(),
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(tenant_id: str) -> list[User]:
        return (
            db.session.query(User)
            .filter(User.tenant_id == tenant_id)
            .order_by(User.created_at.asc())
            .all()
        )

    @staticmethod
    def add(user: User) -> User:
        db.session.add(user)
        return user

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def flush():
        db.session.flush()