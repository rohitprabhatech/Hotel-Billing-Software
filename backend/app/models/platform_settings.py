"""Platform-wide SaaS settings (singleton row)."""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.base import TimestampMixin

PLATFORM_SETTINGS_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_TRIAL_DAYS = 15
DEFAULT_EXPIRY_WARNING_DAYS = 5
MIN_TRIAL_DAYS = 1
MAX_TRIAL_DAYS = 365
MIN_EXPIRY_WARNING_DAYS = 1
MAX_EXPIRY_WARNING_DAYS = 30


class PlatformSettings(db.Model, TimestampMixin):
    __tablename__ = "platform_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=PLATFORM_SETTINGS_ID)
    trial_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    trial_days: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_TRIAL_DAYS)
    expiry_warning_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_EXPIRY_WARNING_DAYS
    )
