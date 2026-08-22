"""Restaurant order channels and statuses (BIZ-13)."""

ORDER_CHANNEL_DINE_IN = "dine_in"
ORDER_CHANNEL_TAKEAWAY = "takeaway"
ORDER_CHANNEL_DELIVERY = "delivery"

ALLOWED_ORDER_CHANNELS: frozenset[str] = frozenset(
    {
        ORDER_CHANNEL_DINE_IN,
        ORDER_CHANNEL_TAKEAWAY,
        ORDER_CHANNEL_DELIVERY,
    }
)

ORDER_CHANNEL_LABELS: dict[str, str] = {
    ORDER_CHANNEL_DINE_IN: "Dine-in",
    ORDER_CHANNEL_TAKEAWAY: "Takeaway",
    ORDER_CHANNEL_DELIVERY: "Delivery",
}

ORDER_STATUS_OPEN = "OPEN"
ORDER_STATUS_CANCELLED = "CANCELLED"
ORDER_STATUS_BILLED = "BILLED"

ALLOWED_ORDER_STATUSES: frozenset[str] = frozenset(
    {
        ORDER_STATUS_OPEN,
        ORDER_STATUS_CANCELLED,
        ORDER_STATUS_BILLED,
    }
)


def assert_valid_order_channel(channel: str) -> str:
    cleaned = (channel or "").strip().lower()
    if cleaned not in ALLOWED_ORDER_CHANNELS:
        raise ValueError(
            "Invalid order channel. Allowed: dine_in, takeaway, delivery"
        )
    return cleaned
