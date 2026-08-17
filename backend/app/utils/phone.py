"""Phone normalization for WhatsApp / E.164 (multi-country, no India-only hardcode)."""

from __future__ import annotations

import re

from app.utils.exceptions import ValidationError

_DIGITS = re.compile(r"\D+")


def digits_only(value: str | None) -> str:
    return _DIGITS.sub("", value or "")


def mask_e164(e164: str | None) -> str | None:
    """Mask for UI/audit: +91******3210."""
    if not e164:
        return None
    raw = e164.strip()
    if not raw.startswith("+"):
        raw = f"+{digits_only(raw)}"
    body = digits_only(raw)
    if len(body) < 6:
        return raw
    visible = body[-4:]
    cc_len = max(1, len(body) - 10)  # rough: last 10 national, rest country
    # Prefer keeping leading + and country hint, mask middle
    if len(body) <= 8:
        return f"+{'*' * (len(body) - 2)}{body[-2:]}"
    prefix = body[: min(cc_len, 3)]
    return f"+{prefix}{'*' * max(4, len(body) - len(prefix) - 4)}{visible}"


def normalize_phone(
    *,
    country_code: str | None = None,
    national_number: str | None = None,
    e164: str | None = None,
) -> dict:
    """
    Normalize to E.164 components.

    Accepts either:
    - country_code + national_number, or
    - a full e164 / international string in e164 (or national_number if it starts with +)
    """
    if e164 and str(e164).strip():
        combined = str(e164).strip()
    elif national_number and str(national_number).strip().startswith("+"):
        combined = str(national_number).strip()
    else:
        cc = digits_only(country_code)
        nat = digits_only(national_number)
        if not cc:
            raise ValidationError("Country code is required for WhatsApp delivery.")
        if not nat:
            raise ValidationError("Customer mobile number is required for WhatsApp delivery.")
        if len(cc) < 1 or len(cc) > 3:
            raise ValidationError("Invalid country code.")
        if len(nat) < 6 or len(nat) > 14:
            raise ValidationError("Invalid mobile number length.")
        if nat.startswith("0"):
            nat = nat.lstrip("0")
            if len(nat) < 6:
                raise ValidationError("Invalid mobile number.")
        full = f"{cc}{nat}"
        if len(full) < 8 or len(full) > 15:
            raise ValidationError("Invalid phone number for WhatsApp.")
        return {
            "country_code": cc,
            "national": nat,
            "e164": f"+{full}",
            "masked": mask_e164(f"+{full}"),
        }

    # Parse international / E.164-ish input
    cleaned = combined.strip()
    if cleaned.startswith("00"):
        cleaned = f"+{cleaned[2:]}"
    body = digits_only(cleaned)
    if len(body) < 8 or len(body) > 15:
        raise ValidationError("Invalid phone number for WhatsApp.")

    cc = digits_only(country_code) if country_code else None
    if cc and body.startswith(cc) and len(body) > len(cc) + 5:
        nat = body[len(cc) :]
    else:
        # Heuristic: if 11–15 digits and starts with known-length, keep last 10 as national when possible
        if len(body) > 10:
            cc = body[:-10]
            nat = body[-10:]
        else:
            # Require explicit country when ambiguous short numbers
            if not cc:
                raise ValidationError(
                    "Country code is required. Enter country code and mobile number separately."
                )
            nat = body
            if nat.startswith(cc):
                nat = nat[len(cc) :]
    if len(cc) < 1 or len(cc) > 3:
        raise ValidationError("Invalid country code.")
    if len(nat) < 6 or len(nat) > 14:
        raise ValidationError("Invalid mobile number length.")
    full = f"{cc}{nat}"
    return {
        "country_code": cc,
        "national": nat,
        "e164": f"+{full}",
        "masked": mask_e164(f"+{full}"),
    }
