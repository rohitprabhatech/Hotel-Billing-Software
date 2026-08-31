"""Controlled business type catalog for tenants (exactly 14).

Selectable labels only — not hardcoded into billing math.
Medical Store / pharmacy codes are permanently excluded.
"""

from __future__ import annotations

# Canonical codes (Sprint BIZ-01). Exactly 14. No "other". No medical.
BUSINESS_TYPES: tuple[tuple[str, str], ...] = (
    ("hotel_restaurant", "Hotels / Restaurants"),
    ("cafe_tea", "Cafes / Tea Shops"),
    ("grocery_kirana", "Grocery / Kirana"),
    ("clothing", "Clothing Shops"),
    ("mobile", "Mobile Shops"),
    ("hardware", "Hardware / Building Material"),
    ("bakery_sweet", "Bakery / Sweet Shops"),
    ("stationery", "Stationery Shops"),
    ("electronics", "Electronics Shops"),
    ("furniture", "Furniture Shops"),
    ("book_store", "Book Stores"),
    ("wholesale", "Wholesale Shops"),
    ("travel_agency", "Travel Agencies"),
)

ALLOWED_BUSINESS_TYPES = frozenset(code for code, _ in BUSINESS_TYPES)

# DB / model default when a value is somehow blank after migration.
# Registration still requires an explicit selection (no silent "other").
DEFAULT_BUSINESS_TYPE = "grocery_kirana"

# FSSAI UI/print guidance for food-service oriented types.
FSSAI_RELEVANT_TYPES = frozenset(
    {
        "hotel_restaurant",
        "cafe_tea",
        "bakery_sweet",
    }
)

# Legacy → canonical (pre–BIZ-01 codes). Used for data migration and safe reads.
LEGACY_BUSINESS_TYPE_MAP: dict[str, str] = {
    "restaurant": "hotel_restaurant",
    "hotel": "hotel_restaurant",
    "clothing_store": "clothing",
    "footwear_store": "clothing",
    "kirana_store": "grocery_kirana",
    "grocery_store": "grocery_kirana",
    "electronics_store": "electronics",
    "retail_shop": "stationery",
    "other": "grocery_kirana",
    # Doc aliases sometimes used in packs
    "bakery_sweets": "bakery_sweet",
    "bookstore": "book_store",
    "building_material": "hardware",
}

# Permanently rejected (never map into catalog).
EXCLUDED_BUSINESS_TYPES = frozenset(
    {
        "medical",
        "medical_store",
        "pharmacy",
        "chemist",
        "drugstore",
        "medicine_store",
    }
)


def _clean(value) -> str:
    return str(value).strip().lower() if value is not None else ""


def map_legacy_business_type(value) -> str | None:
    """Return canonical code if value is canonical or known legacy; else None."""
    code = _clean(value)
    if not code:
        return None
    if code in EXCLUDED_BUSINESS_TYPES:
        return None
    if code in ALLOWED_BUSINESS_TYPES:
        return code
    mapped = LEGACY_BUSINESS_TYPE_MAP.get(code)
    if mapped in ALLOWED_BUSINESS_TYPES:
        return mapped
    return None


def coerce_business_type(value) -> str:
    """Best-effort canonical code for reads/labels (never raises for blank)."""
    mapped = map_legacy_business_type(value)
    if mapped:
        return mapped
    return DEFAULT_BUSINESS_TYPE


def normalize_business_type(value, *, allow_legacy: bool = False) -> str:
    """Validate business type for writes.

    - New registrations / settings: ``allow_legacy=False`` → only the 14 codes.
    - Data migration helpers may pass ``allow_legacy=True`` to accept old codes.
    """
    code = _clean(value)
    if not code:
        raise ValueError("Business type is required. Choose one of the 14 supported types.")
    if code in EXCLUDED_BUSINESS_TYPES:
        raise ValueError(
            "Medical Store / pharmacy business types are not supported."
        )
    if code in ALLOWED_BUSINESS_TYPES:
        return code
    if allow_legacy:
        mapped = LEGACY_BUSINESS_TYPE_MAP.get(code)
        if mapped:
            return mapped
    raise ValueError(
        "Invalid business type. Choose a supported business type from the catalog."
    )


def business_type_label(value: str | None) -> str:
    code = coerce_business_type(value)
    for item_code, label in BUSINESS_TYPES:
        if item_code == code:
            return label
    return BUSINESS_TYPES[2][1]  # Grocery / Kirana fallback label


def is_fssai_relevant(value: str | None) -> bool:
    return coerce_business_type(value) in FSSAI_RELEVANT_TYPES


def list_business_types() -> list[dict]:
    return [
        {
            "code": code,
            "label": label,
            "fssai_relevant": code in FSSAI_RELEVANT_TYPES,
        }
        for code, label in BUSINESS_TYPES
    ]


def legacy_mapping_table() -> list[dict]:
    """Documented mapping for ops / docs (legacy → canonical)."""
    return [
        {"legacy": legacy, "canonical": canonical}
        for legacy, canonical in sorted(LEGACY_BUSINESS_TYPE_MAP.items())
    ]
