"""Dining table statuses and transition rules (BIZ-12)."""

TABLE_STATUS_AVAILABLE = "available"
TABLE_STATUS_OCCUPIED = "occupied"
TABLE_STATUS_RESERVED = "reserved"
TABLE_STATUS_BILL_PENDING = "bill_pending"

ALLOWED_TABLE_STATUSES: frozenset[str] = frozenset(
    {
        TABLE_STATUS_AVAILABLE,
        TABLE_STATUS_OCCUPIED,
        TABLE_STATUS_RESERVED,
        TABLE_STATUS_BILL_PENDING,
    }
)

TABLE_STATUS_LABELS: dict[str, str] = {
    TABLE_STATUS_AVAILABLE: "Available",
    TABLE_STATUS_OCCUPIED: "Occupied",
    TABLE_STATUS_RESERVED: "Reserved",
    TABLE_STATUS_BILL_PENDING: "Bill Pending",
}

# Valid direct status transitions for a standalone (non-merged-secondary) table.
TABLE_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    TABLE_STATUS_AVAILABLE: frozenset(
        {TABLE_STATUS_OCCUPIED, TABLE_STATUS_RESERVED}
    ),
    TABLE_STATUS_OCCUPIED: frozenset(
        {TABLE_STATUS_AVAILABLE, TABLE_STATUS_BILL_PENDING}
    ),
    TABLE_STATUS_RESERVED: frozenset(
        {TABLE_STATUS_AVAILABLE, TABLE_STATUS_OCCUPIED}
    ),
    TABLE_STATUS_BILL_PENDING: frozenset(
        {TABLE_STATUS_AVAILABLE, TABLE_STATUS_OCCUPIED}
    ),
}


def assert_valid_table_status(status: str) -> str:
    cleaned = (status or "").strip().lower()
    if cleaned not in ALLOWED_TABLE_STATUSES:
        raise ValueError(
            f"Invalid table status. Allowed: {', '.join(sorted(ALLOWED_TABLE_STATUSES))}"
        )
    return cleaned


def can_transition_table_status(current: str, new: str) -> bool:
    current_norm = assert_valid_table_status(current)
    new_norm = assert_valid_table_status(new)
    if current_norm == new_norm:
        return True
    return new_norm in TABLE_STATUS_TRANSITIONS.get(current_norm, frozenset())
