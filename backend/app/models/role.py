"""Global role model — OWNER and BILLING_USER only."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin

ROLE_OWNER = "OWNER"
ROLE_BILLING_USER = "BILLING_USER"
VALID_ROLES = {ROLE_OWNER, ROLE_BILLING_USER}


class Role(db.Model, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    users = relationship("User", back_populates="role", lazy="dynamic")