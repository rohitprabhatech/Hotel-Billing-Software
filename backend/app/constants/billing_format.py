"""Printed bill layout variants."""

from __future__ import annotations

STANDARD = "standard"
TRAVEL = "travel"

ALLOWED_BILL_FORMATS: frozenset[str] = frozenset({STANDARD, TRAVEL})

BILL_FORMAT_LABELS: dict[str, str] = {
    STANDARD: "Standard Cash Memo",
    TRAVEL: "Travel Booking Voucher",
}

DEFAULT_BILL_FORMAT_BY_BUSINESS: dict[str, str] = {
    "travel_agency": TRAVEL,
}


def default_bill_format(business_type: str | None) -> str:
    if not business_type:
        return STANDARD
    return DEFAULT_BILL_FORMAT_BY_BUSINESS.get(str(business_type).strip().lower(), STANDARD)


def normalize_bill_format(value, *, business_type: str | None = None) -> str:
    if value is None or str(value).strip() == "":
        return default_bill_format(business_type)
    key = str(value).strip().lower()
    if key not in ALLOWED_BILL_FORMATS:
        raise ValueError(f"bill_format must be one of: {', '.join(sorted(ALLOWED_BILL_FORMATS))}")
    return key


def bill_format_label(value: str | None) -> str:
    key = normalize_bill_format(value) if value else STANDARD
    return BILL_FORMAT_LABELS.get(key, key)
