"""Performance budgets for list/POS hot paths (BIZ-66)."""

# POS catalog window — keep DOM + query cost bounded.
POS_CATALOG_DEFAULT_LIMIT = 50
POS_CATALOG_MAX_LIMIT = 100

# Staging acceptance target for barcode exact + short-q POS search (p95).
POS_SEARCH_P95_MS = 200

# Restaurant menu catalog hard cap (was unbounded).
MENU_CATALOG_MAX = 500


def clamp_pos_catalog_limit(limit) -> int:
    try:
        value = int(limit if limit is not None else POS_CATALOG_DEFAULT_LIMIT)
    except (TypeError, ValueError):
        value = POS_CATALOG_DEFAULT_LIMIT
    return min(max(value, 1), POS_CATALOG_MAX_LIMIT)
