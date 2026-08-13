"""Role data access."""

from app.extensions import db
from app.models.role import Role


class RoleRepository:
    @staticmethod
    def get_by_name(name: str) -> Role | None:
        return db.session.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_by_id(role_id: str) -> Role | None:
        return db.session.get(Role, role_id)

    @staticmethod
    def list_all() -> list[Role]:
        return db.session.query(Role).order_by(Role.name.asc()).all()