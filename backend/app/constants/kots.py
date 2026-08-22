"""Kitchen Order Ticket statuses and transition rules (BIZ-14)."""

KOT_STATUS_QUEUED = "queued"
KOT_STATUS_PREPARING = "preparing"
KOT_STATUS_READY = "ready"

ALLOWED_KOT_STATUSES: frozenset[str] = frozenset(
    {
        KOT_STATUS_QUEUED,
        KOT_STATUS_PREPARING,
        KOT_STATUS_READY,
    }
)

KOT_STATUS_LABELS: dict[str, str] = {
    KOT_STATUS_QUEUED: "Queued",
    KOT_STATUS_PREPARING: "Preparing",
    KOT_STATUS_READY: "Ready",
}

KOT_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    KOT_STATUS_QUEUED: frozenset({KOT_STATUS_PREPARING, KOT_STATUS_READY}),
    KOT_STATUS_PREPARING: frozenset({KOT_STATUS_READY}),
    KOT_STATUS_READY: frozenset(),
}

ACTIVE_KOT_STATUSES: frozenset[str] = frozenset(
    {KOT_STATUS_QUEUED, KOT_STATUS_PREPARING, KOT_STATUS_READY}
)


def assert_valid_kot_status(status: str) -> str:
    cleaned = (status or "").strip().lower()
    if cleaned not in ALLOWED_KOT_STATUSES:
        raise ValueError(
            f"Invalid KOT status. Allowed: {', '.join(sorted(ALLOWED_KOT_STATUSES))}"
        )
    return cleaned


def can_transition_kot_status(current: str, new: str) -> bool:
    current_norm = assert_valid_kot_status(current)
    new_norm = assert_valid_kot_status(new)
    if current_norm == new_norm:
        return True
    return new_norm in KOT_STATUS_TRANSITIONS.get(current_norm, frozenset())
