"""Platform settings data access."""

from app.extensions import db
from app.models.platform_settings import PLATFORM_SETTINGS_ID, PlatformSettings


class PlatformSettingsRepository:
    @staticmethod
    def get() -> PlatformSettings | None:
        return db.session.get(PlatformSettings, PLATFORM_SETTINGS_ID)

    @staticmethod
    def add(row: PlatformSettings) -> PlatformSettings:
        db.session.add(row)
        return row
