"""Tenant (business) model."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.business_types import DEFAULT_BUSINESS_TYPE
from app.extensions import db
from app.models.base import TimestampMixin


class Tenant(db.Model, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[str] = mapped_column(
        String(40), nullable=False, default=DEFAULT_BUSINESS_TYPE
    )
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    pincode: Mapped[str | None] = mapped_column(String(20))
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    gst_number: Mapped[str | None] = mapped_column(String(30))
    fssai_number: Mapped[str | None] = mapped_column(String(50))
    bill_number_prefix: Mapped[str | None] = mapped_column(String(20))
    default_gst_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    bill_paper_size: Mapped[str | None] = mapped_column(String(20))
    bill_width_mm: Mapped[int | None] = mapped_column(Integer)
    bill_height_mm: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    users = relationship("User", back_populates="tenant", lazy="dynamic")

    def is_active(self) -> bool:
        return self.status == "ACTIVE"