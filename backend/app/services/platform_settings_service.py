"""Global trial / expiry-warning settings (singleton)."""

from app.extensions import db
from app.models.platform_settings import (
    DEFAULT_EXPIRY_WARNING_DAYS,
    DEFAULT_TRIAL_DAYS,
    MAX_EXPIRY_WARNING_DAYS,
    MAX_TRIAL_DAYS,
    MIN_EXPIRY_WARNING_DAYS,
    MIN_TRIAL_DAYS,
    PLATFORM_SETTINGS_ID,
    PlatformSettings,
)
from app.repositories.platform_settings_repository import PlatformSettingsRepository
from app.utils.exceptions import ValidationError
from app.utils.request_context import require_master_context


class PlatformSettingsService:
    @staticmethod
    def get_or_create() -> PlatformSettings:
        row = PlatformSettingsRepository.get()
        if row is None:
            row = PlatformSettings(
                id=PLATFORM_SETTINGS_ID,
                trial_enabled=True,
                trial_days=DEFAULT_TRIAL_DAYS,
                expiry_warning_days=DEFAULT_EXPIRY_WARNING_DAYS,
            )
            PlatformSettingsRepository.add(row)
            db.session.flush()
        return row

    @staticmethod
    def get_public_view() -> dict:
        row = PlatformSettingsService.get_or_create()
        return PlatformSettingsService.serialize(row)

    @staticmethod
    def get_for_master() -> dict:
        require_master_context()
        return PlatformSettingsService.get_public_view()

    @staticmethod
    def update(
        *,
        trial_enabled: bool,
        trial_days: int,
        expiry_warning_days: int | None = None,
    ) -> dict:
        require_master_context()
        days = int(trial_days)
        if days < MIN_TRIAL_DAYS or days > MAX_TRIAL_DAYS:
            raise ValidationError(
                f"Trial duration must be between {MIN_TRIAL_DAYS} and {MAX_TRIAL_DAYS} days"
            )
        row = PlatformSettingsService.get_or_create()
        row.trial_enabled = bool(trial_enabled)
        row.trial_days = days
        if expiry_warning_days is not None:
            warning = int(expiry_warning_days)
            if warning < MIN_EXPIRY_WARNING_DAYS or warning > MAX_EXPIRY_WARNING_DAYS:
                raise ValidationError(
                    "Expiry warning must be between "
                    f"{MIN_EXPIRY_WARNING_DAYS} and {MAX_EXPIRY_WARNING_DAYS} days"
                )
            row.expiry_warning_days = warning
        db.session.commit()
        return PlatformSettingsService.serialize(row)

    @staticmethod
    def serialize(row: PlatformSettings) -> dict:
        return {
            "trial_enabled": bool(row.trial_enabled),
            "trial_days": int(row.trial_days),
            "expiry_warning_days": int(row.expiry_warning_days),
        }
