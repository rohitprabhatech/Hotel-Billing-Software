"""Scrub secrets and sensitive PII from audit JSON snapshots (BIZ-65)."""

from __future__ import annotations

_SECRET_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "confirm_password",
        "current_password",
        "new_password",
        "access_token",
        "refresh_token",
        "token",
        "secret",
        "access_token_encrypted",
        "api_key",
        "otp",
        "pin",
    }
)

# Redact value but keep key so owners see that a field changed.
_REDACT_KEYS = frozenset(
    {
        "document_number",
        "passport_number",
        "id_number",
        "aadhaar",
        "pan",
        "card_number",
        "cvv",
    }
)

_REDACTED = "[REDACTED]"


def scrub_audit_payload(value):
    """Recursively remove secrets and mask PII fields in audit old/new data."""
    if value is None:
        return None
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in _SECRET_KEYS:
                continue
            if lowered in _REDACT_KEYS:
                cleaned[key] = _REDACTED if item not in (None, "") else item
            else:
                cleaned[key] = scrub_audit_payload(item)
        return cleaned
    if isinstance(value, list):
        return [scrub_audit_payload(item) for item in value]
    return value
