"""Controlled business type options for tenants.

These are selectable labels/options — not hardcoded into billing calculation logic.
"""

BUSINESS_TYPE_OTHER = "other"

BUSINESS_TYPES = (
    ("restaurant", "Restaurant"),
    ("hotel", "Hotel"),
    ("clothing_store", "Clothing Store"),
    ("footwear_store", "Footwear Store"),
    ("kirana_store", "Kirana Store"),
    ("grocery_store", "Grocery Store"),
    ("electronics_store", "Electronics Store"),
    ("retail_shop", "Retail Shop"),
    (BUSINESS_TYPE_OTHER, "Other"),
)

ALLOWED_BUSINESS_TYPES = frozenset(code for code, _ in BUSINESS_TYPES)
DEFAULT_BUSINESS_TYPE = BUSINESS_TYPE_OTHER

# FSSAI is relevant for food-service oriented businesses only (UI guidance).
FSSAI_RELEVANT_TYPES = frozenset({"restaurant", "hotel"})


def normalize_business_type(value) -> str:
    code = (str(value).strip().lower() if value is not None else "")
    if not code:
        return DEFAULT_BUSINESS_TYPE
    if code not in ALLOWED_BUSINESS_TYPES:
        raise ValueError(
            "Invalid business type. Choose a supported business type or Other."
        )
    return code


def business_type_label(value: str | None) -> str:
    code = normalize_business_type(value) if value else DEFAULT_BUSINESS_TYPE
    for item_code, label in BUSINESS_TYPES:
        if item_code == code:
            return label
    return "Other"


def is_fssai_relevant(value: str | None) -> bool:
    try:
        code = normalize_business_type(value)
    except ValueError:
        code = DEFAULT_BUSINESS_TYPE
    return code in FSSAI_RELEVANT_TYPES


def list_business_types() -> list[dict]:
    return [
        {
            "code": code,
            "label": label,
            "fssai_relevant": code in FSSAI_RELEVANT_TYPES,
        }
        for code, label in BUSINESS_TYPES
    ]
