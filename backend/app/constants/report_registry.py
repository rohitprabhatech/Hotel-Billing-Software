"""Module-aware report registry for the common Reports hub (BIZ-61).

Keep this catalog small: every entry must map to an existing API or UI route.
Do not add speculative industry reports here.
"""

from __future__ import annotations

from typing import Any

# Max inclusive calendar days for custom report ranges (perf budget).
MAX_CUSTOM_RANGE_DAYS = 366

# Bills list page size defaults for report payloads.
DEFAULT_BILLS_PER_PAGE = 50
MAX_BILLS_PER_PAGE = 200

# kind:
#   hub  — rendered inside /owner/reports (ReportsPage view key)
#   link — separate page; shown in hub as a deep-link card
REPORT_REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "id": "sales",
        "label": "Sales",
        "description": "Daily, weekly, monthly, and custom sales with export",
        "group": "core",
        "kind": "hub",
        "view": "sales",
        "modules": frozenset({"core_reports"}),
        "api_path": "/reports/daily-sales",
        "sort_order": 10,
    },
    {
        "id": "fb",
        "label": "F&B Insights",
        "description": "Channel, table, and wastage summaries",
        "group": "industry",
        "kind": "hub",
        "view": "fb",
        "modules": frozenset({"order_channels"}),
        "api_path": "/reports/fb",
        "sort_order": 20,
    },
    {
        "id": "kirana",
        "label": "Kirana",
        "description": "Grocery daily sales and udhari outstanding snapshot",
        "group": "industry",
        "kind": "hub",
        "view": "kirana",
        "modules": frozenset({"customer_credit"}),
        "api_path": "/grocery/sales",
        "sort_order": 30,
    },
    {
        "id": "apparel",
        "label": "Apparel",
        "description": "Sales by brand, size, color, and variant stock",
        "group": "industry",
        "kind": "hub",
        "view": "apparel",
        "modules": frozenset({"variants"}),
        "api_path": "/clothing/sales",
        "sort_order": 40,
    },
    {
        "id": "mobile",
        "label": "Mobile / Electronics",
        "description": "Sales by brand/model with IMEI stock",
        "group": "industry",
        "kind": "hub",
        "view": "mobile",
        "modules": frozenset({"serial_imei"}),
        "api_path": "/mobile/sales",
        "sort_order": 50,
    },
    {
        "id": "outstanding",
        "label": "Outstanding / Aging",
        "description": "Aged customer and supplier dues",
        "group": "industry",
        "kind": "link",
        "modules": frozenset({"customer_credit"}),
        "ui_path": "/owner/outstanding",
        "api_path": "/reports/outstanding",
        "sort_order": 60,
    },
    {
        "id": "travel_commission",
        "label": "Travel Commission",
        "description": "Agent commission report and entries",
        "group": "industry",
        "kind": "link",
        "modules": frozenset({"travel_commission"}),
        "ui_path": "/owner/travel-agents",
        "api_path": "/commissions/report",
        "sort_order": 70,
    },
    {
        "id": "tour_packages",
        "label": "Tour Packages",
        "description": "Package catalog and service billing",
        "group": "industry",
        "kind": "link",
        "modules": frozenset({"tour_packages"}),
        "ui_path": "/owner/tour-packages",
        "api_path": "/tour-packages",
        "sort_order": 80,
    },
    {
        "id": "travel_bookings",
        "label": "Travel Bookings",
        "description": "Booking board, advances, and trip status",
        "group": "industry",
        "kind": "link",
        "modules": frozenset({"travel_bookings"}),
        "ui_path": "/owner/travel-bookings",
        "api_path": "/travel-bookings",
        "sort_order": 90,
    },
)


def serialize_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "label": entry["label"],
        "description": entry["description"],
        "group": entry["group"],
        "kind": entry["kind"],
        "view": entry.get("view"),
        "modules": sorted(entry["modules"]),
        "api_path": entry.get("api_path"),
        "ui_path": entry.get("ui_path"),
        "sort_order": entry["sort_order"],
    }


def filter_registry_for_modules(enabled_modules: set[str] | frozenset[str]) -> list[dict[str, Any]]:
    enabled = {str(code).strip().lower() for code in enabled_modules}
    rows = []
    for entry in REPORT_REGISTRY:
        if entry["modules"] & enabled:
            rows.append(serialize_registry_entry(entry))
    rows.sort(key=lambda row: (row["sort_order"], row["label"]))
    return rows
