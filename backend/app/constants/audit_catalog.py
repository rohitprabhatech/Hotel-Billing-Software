"""Tenant audit catalog — modules, entity types, and industry actions (BIZ-65)."""

from __future__ import annotations

# Module → entity_type codes used in audit_logs.entity_type
AUDIT_MODULES: dict[str, dict] = {
    "core": {
        "label": "Core billing & catalog",
        "entity_types": [
            "BILL",
            "ITEM",
            "CATEGORY",
            "CUSTOMER",
            "SUPPLIER",
            "PURCHASE",
            "EXPENSE",
            "USER",
            "TENANT",
            "STOCK_MOVEMENT",
        ],
    },
    "fb": {
        "label": "F&B / cafe",
        "entity_types": ["ORDER", "KOT", "DINING_TABLE", "RECIPE", "WASTAGE", "ADDON"],
    },
    "serial": {
        "label": "Serial / IMEI & repairs",
        "entity_types": ["SERIAL_UNIT", "REPAIR_ORDER", "INSTALLATION_ORDER"],
    },
    "trade_docs": {
        "label": "Quotations & challans",
        "entity_types": ["QUOTATION", "DELIVERY_CHALLAN"],
    },
    "warehouse": {
        "label": "Warehouses & transfers",
        "entity_types": ["WAREHOUSE", "STOCK_TRANSFER", "WAREHOUSE_STOCK"],
    },
    "bakery_furniture": {
        "label": "Custom orders & production",
        "entity_types": ["CUSTOM_ORDER", "PRODUCTION", "DELIVERY_JOB"],
    },
    "wholesale": {
        "label": "Wholesale",
        "entity_types": ["PRICE_LIST", "SALES_ORDER", "PURCHASE_ORDER"],
    },
    "travel": {
        "label": "Travel agency",
        "entity_types": [
            "TOUR_PACKAGE",
            "TRAVEL_BOOKING",
            "TRAVEL_AGENT",
            "TRAVEL_COMMISSION_ENTRY",
            "TRAVEL_ITINERARY_ITEM",
            "TRAVEL_BOOKING_DOCUMENT",
        ],
    },
}

INDUSTRY_AUDIT_ACTIONS: list[str] = [
    "CREATE_KOT",
    "REPRINT_KOT",
    "UPDATE_KOT_STATUS",
    "CREATE_REPAIR",
    "UPDATE_REPAIR_STATUS",
    "CREATE_INSTALLATION",
    "UPDATE_INSTALLATION_STATUS",
    "CREATE_QUOTATION",
    "UPDATE_QUOTATION_STATUS",
    "CONVERT_QUOTATION",
    "CREATE_DELIVERY_CHALLAN",
    "UPDATE_DELIVERY_CHALLAN_STATUS",
    "CONVERT_DELIVERY_CHALLAN",
    "CREATE_WAREHOUSE",
    "UPDATE_WAREHOUSE",
    "CREATE_STOCK_TRANSFER",
    "ADJUST_WAREHOUSE_STOCK",
    "CREATE_CUSTOM_ORDER",
    "CUSTOM_ORDER_ADVANCE",
    "UPDATE_CUSTOM_ORDER_STATUS",
    "CREATE_PRODUCTION",
    "CREATE_DELIVERY_JOB",
    "UPDATE_DELIVERY_STATUS",
    "CREATE_PRICE_LIST",
    "UPDATE_PRICE_LIST",
    "DELETE_PRICE_LIST",
    "REPLACE_PRICE_LIST_ITEMS",
    "CREATE_SALES_ORDER",
    "UPDATE_SALES_ORDER_STATUS",
    "CONVERT_SALES_ORDER",
    "CREATE_PURCHASE_ORDER",
    "UPDATE_PURCHASE_ORDER_STATUS",
    "CONVERT_PURCHASE_ORDER",
    "CREATE_TOUR_PACKAGE",
    "UPDATE_TOUR_PACKAGE",
    "BILL_TOUR_PACKAGE",
    "CREATE_TRAVEL_BOOKING",
    "TRAVEL_BOOKING_PAYMENT",
    "UPDATE_TRAVEL_BOOKING_STATUS",
    "CREATE_TRAVEL_AGENT",
    "UPDATE_TRAVEL_AGENT",
    "CREATE_TRAVEL_COMMISSION",
    "UPDATE_TRAVEL_COMMISSION",
    "UPDATE_TRAVEL_COMMISSION_STATUS",
    "CREATE_TRAVEL_ITINERARY_ITEM",
    "UPDATE_TRAVEL_ITINERARY_ITEM",
    "DELETE_TRAVEL_ITINERARY_ITEM",
    "CREATE_TRAVEL_BOOKING_DOCUMENT",
    "DELETE_TRAVEL_BOOKING_DOCUMENT",
]


def entity_types_for_module(module: str | None) -> list[str] | None:
    if not module:
        return None
    key = str(module).strip().lower()
    row = AUDIT_MODULES.get(key)
    if row is None:
        return None
    return list(row["entity_types"])


def list_audit_meta() -> dict:
    modules = [
        {
            "key": key,
            "label": meta["label"],
            "entity_types": list(meta["entity_types"]),
        }
        for key, meta in AUDIT_MODULES.items()
    ]
    entity_types = sorted(
        {et for meta in AUDIT_MODULES.values() for et in meta["entity_types"]}
    )
    return {
        "modules": modules,
        "entity_types": entity_types,
        "industry_actions": list(INDUSTRY_AUDIT_ACTIONS),
    }
