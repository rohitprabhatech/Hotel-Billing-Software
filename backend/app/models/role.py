"""Global role model — OWNER, MANAGER, and BILLING_USER."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin

ROLE_OWNER = "OWNER"
ROLE_MANAGER = "MANAGER"
ROLE_BILLING_USER = "BILLING_USER"
VALID_ROLES = {ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER}

# Default UUID used in seeds/migrations for the Manager role row.
ROLE_MANAGER_ID = "33333333-3333-3333-3333-333333333333"


class Role(db.Model, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    users = relationship("User", back_populates="role", lazy="dynamic")
