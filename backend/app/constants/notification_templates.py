"""Module-aware notification templates (BIZ-63).

Central registry of industry/core in-app notification keys.
Emitters call `NotificationService.emit_template` so title/message stay consistent
and duplicate spam is rate-limited per tenant + type + entity.
"""

from __future__ import annotations

from typing import Any

# Default: skip re-emit while an unread alert for the same type+entity is open.
# Optional cooldown_seconds also blocks recent emits (read or unread).
NOTIFICATION_TEMPLATES: dict[str, dict[str, Any]] = {
    "low_stock": {
        "type": "LOW_STOCK",
        "module": "core_inventory",
        "title": "Low stock",
        "message": (
            "Low stock: {name} has only {stock:g} units remaining "
            "(minimum {minimum:g})."
        ),
        "entity_type": "ITEM",
        "dedupe_open": True,
        "industry": False,
    },
    "out_of_stock": {
        "type": "OUT_OF_STOCK",
        "module": "core_inventory",
        "title": "Out of stock",
        "message": "Out of stock: {name} is currently unavailable.",
        "entity_type": "ITEM",
        "dedupe_open": True,
        "industry": False,
    },
    "kot_ready": {
        "type": "KOT_READY",
        "module": "kot",
        "title": "KOT ready",
        "message": "{kot_number}: order {order_number} is ready for service{table_part}.",
        "entity_type": "KOT",
        "dedupe_open": True,
        "cooldown_seconds": 120,
        "industry": True,
        "event": "Kitchen ticket marked ready",
    },
    "repair_ready": {
        "type": "REPAIR_READY",
        "module": "repair_service",
        "title": "Repair ready",
        "message": "{repair_number}: {serial} is ready for customer pickup.",
        "entity_type": "REPAIR_ORDER",
        "dedupe_open": True,
        "industry": True,
        "event": "Repair marked ready",
    },
    "batch_expiring": {
        "type": "BATCH_EXPIRING",
        "module": "batch_expiry",
        "title": "Expiring soon: {item_name}",
        "message": (
            "Batch {batch_code} expires on {expiry_date} "
            "({days_left} day(s) left, qty {quantity:g})."
        ),
        "entity_type": "ITEM_BATCH",
        "dedupe_open": True,
        "industry": True,
        "event": "Batch within expiry warning window",
    },
    "batch_expired": {
        "type": "BATCH_EXPIRED",
        "module": "batch_expiry",
        "title": "Expired batch: {item_name}",
        "message": (
            "Batch {batch_code} expired on {expiry_date} (qty {quantity:g})."
        ),
        "entity_type": "ITEM_BATCH",
        "dedupe_open": True,
        "industry": True,
        "event": "Batch past expiry date",
    },
    "travel_payment_due": {
        "type": "TRAVEL_PAYMENT_DUE",
        "module": "travel_bookings",
        "title": "Travel payment due",
        "message": (
            "{booking_number}: {customer_name} has ₹{remaining:.2f} remaining."
        ),
        "entity_type": "TRAVEL_BOOKING",
        "dedupe_open": False,
        "cooldown_seconds": 300,
        "industry": True,
        "event": "Travel booking has outstanding balance",
    },
    "travel_booking_confirmed": {
        "type": "TRAVEL_BOOKING_CONFIRMED",
        "module": "travel_bookings",
        "title": "Travel booking confirmed",
        "message": "{booking_number}: {package_name} confirmed for {customer_name}.",
        "entity_type": "TRAVEL_BOOKING",
        "dedupe_open": True,
        "industry": True,
        "event": "Travel booking status → CONFIRMED",
    },
    "credit_due": {
        "type": "CREDIT_DUE",
        "module": "customer_credit",
        "title": "Credit sale (udhari)",
        "message": (
            "{customer_name}: ₹{amount:.2f} on credit.{bill_part} "
            "Outstanding now ₹{balance_after:.2f}."
        ),
        "entity_type": "CUSTOMER",
        "dedupe_open": False,
        "cooldown_seconds": 60,
        "industry": True,
        "event": "Credit / udhari sale recorded",
    },
    "custom_order_ready": {
        "type": "CUSTOM_ORDER_READY",
        "module": "custom_orders",
        "title": "Custom order ready",
        "message": (
            "{order_number}: {title} is ready for customer pickup/delivery."
        ),
        "entity_type": "CUSTOM_ORDER",
        "dedupe_open": True,
        "industry": True,
        "event": "Custom cake/furniture order ready",
    },
    "installation_scheduled": {
        "type": "INSTALLATION_SCHEDULED",
        "module": "installation",
        "title": "Installation scheduled",
        "message": "{installation_number}: {serial} scheduled for {scheduled_at}.",
        "entity_type": "INSTALLATION_ORDER",
        "dedupe_open": True,
        "industry": True,
        "event": "Installation job scheduled",
    },
}


def list_templates(*, industry_only: bool = False) -> list[dict[str, Any]]:
    rows = []
    for key, tpl in NOTIFICATION_TEMPLATES.items():
        if industry_only and not tpl.get("industry"):
            continue
        rows.append(serialize_template(key, tpl))
    rows.sort(key=lambda row: (not row["industry"], row["module"], row["key"]))
    return rows


def serialize_template(key: str, tpl: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": key,
        "type": tpl["type"],
        "module": tpl["module"],
        "title_template": tpl["title"],
        "message_template": tpl["message"],
        "entity_type": tpl.get("entity_type"),
        "industry": bool(tpl.get("industry")),
        "event": tpl.get("event"),
        "dedupe_open": bool(tpl.get("dedupe_open")),
        "cooldown_seconds": int(tpl.get("cooldown_seconds") or 0),
    }


def get_template(key: str) -> dict[str, Any] | None:
    tpl = NOTIFICATION_TEMPLATES.get(key)
    if tpl is None:
        return None
    return serialize_template(key, tpl)
