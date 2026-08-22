"""Industry / feature module catalog and per-business-type defaults (BIZ-02).

Defaults are code-defined (no DB tables yet). Tenant overrides are reserved for
a later sprint — see docs/00-project-foundation/09-module-feature-matrix.md.
"""

from __future__ import annotations

from app.constants.business_types import ALLOWED_BUSINESS_TYPES, coerce_business_type

# module_code → human label
MODULE_CATALOG: dict[str, str] = {
    # Always-on common core (nav/API available to every tenant)
    "core_billing": "Billing",
    "core_catalog": "Products & Categories",
    "core_inventory": "Inventory & Stock",
    "core_reports": "Sales Reports",
    "core_users": "Users",
    "core_audit": "Audit Logs",
    "core_ai": "AI Assistant",
    "core_settings": "Settings",
    # Industry / shared capability modules
    "restaurant_menu": "Restaurant Menu",
    "table_management": "Table Management",
    "kot": "Kitchen Order Tickets (KOT)",
    "kitchen": "Kitchen Dashboard",
    "order_channels": "Dine-in / Takeaway / Delivery",
    "recipe": "Recipes & Ingredients",
    "wastage": "Wastage Tracking",
    "service_charge": "Service Charge",
    "addons_combos": "Add-ons & Combos",
    "barcode_pos": "Barcode / Fast POS",
    "bulk_pricing": "Bulk Pricing",
    "batch_expiry": "Batch / Expiry",
    "customer_credit": "Customer Credit / Udhari",
    "variants": "Size / Color / Variant Stock",
    "product_images": "Product Images",
    "returns_exchange": "Returns & Exchange",
    "serial_imei": "Serial / IMEI Stock",
    "warranty": "Warranty Tracking",
    "repair_service": "Repair / Service",
    "installation": "Installation Tracking",
    "uom_measurement": "Length / Weight / Area Units",
    "quotation": "Quotations",
    "delivery_challan": "Delivery Challan",
    "warehouse": "Multi-Warehouse Stock",
    "transport_charges": "Transport Charges",
    "production": "Production Runs",
    "custom_orders": "Custom Orders & Advances",
    "delivery_tracking": "Delivery Management",
    "book_metadata": "ISBN / Author / Publisher",
    "price_lists": "Wholesale Price Lists",
    "sales_orders": "Sales Orders",
    "purchase_orders": "Purchase Orders",
    "tour_packages": "Tour Packages",
    "travel_bookings": "Travel Bookings",
    "travel_commission": "Agent Commission",
}

CORE_MODULES: frozenset[str] = frozenset(
    {
        "core_billing",
        "core_catalog",
        "core_inventory",
        "core_reports",
        "core_users",
        "core_audit",
        "core_ai",
        "core_settings",
    }
)

# Per-type industry modules (core modules are always added on resolve).
_BUSINESS_TYPE_INDUSTRY: dict[str, frozenset[str]] = {
    "hotel_restaurant": frozenset(
        {
            "restaurant_menu",
            "table_management",
            "kot",
            "kitchen",
            "order_channels",
            "recipe",
            "wastage",
            "service_charge",
        }
    ),
    "cafe_tea": frozenset(
        {
            "restaurant_menu",
            "table_management",
            "kot",
            "kitchen",
            "order_channels",
            "addons_combos",
            "recipe",
            "wastage",
        }
    ),
    "grocery_kirana": frozenset(
        {
            "barcode_pos",
            "bulk_pricing",
            "batch_expiry",
            "customer_credit",
        }
    ),
    "clothing": frozenset(
        {
            "variants",
            "product_images",
            "returns_exchange",
            "barcode_pos",
        }
    ),
    "mobile": frozenset(
        {
            "serial_imei",
            "warranty",
            "repair_service",
            "returns_exchange",
        }
    ),
    "hardware": frozenset(
        {
            "uom_measurement",
            "bulk_pricing",
            "customer_credit",
            "variants",
        }
    ),
    "bakery_sweet": frozenset(
        {
            "production",
            "recipe",
            "batch_expiry",
            "custom_orders",
            "wastage",
        }
    ),
    "stationery": frozenset(
        {
            "barcode_pos",
            "bulk_pricing",
            "customer_credit",
        }
    ),
    "electronics": frozenset(
        {
            "serial_imei",
            "warranty",
            "repair_service",
            "installation",
            "returns_exchange",
        }
    ),
    "furniture": frozenset(
        {
            "custom_orders",
            "quotation",
            "delivery_tracking",
            "installation",
        }
    ),
    "building_material": frozenset(
        {
            "uom_measurement",
            "quotation",
            "delivery_challan",
            "warehouse",
            "customer_credit",
            "transport_charges",
        }
    ),
    "book_store": frozenset(
        {
            "book_metadata",
            "barcode_pos",
            "bulk_pricing",
            "returns_exchange",
        }
    ),
    "wholesale": frozenset(
        {
            "price_lists",
            "sales_orders",
            "purchase_orders",
            "warehouse",
            "customer_credit",
            "quotation",
            "delivery_challan",
            "barcode_pos",
            "bulk_pricing",
        }
    ),
    "travel_agency": frozenset(
        {
            "tour_packages",
            "travel_bookings",
            "travel_commission",
            "custom_orders",
        }
    ),
}


def assert_module_catalog_complete() -> None:
    missing_types = ALLOWED_BUSINESS_TYPES - set(_BUSINESS_TYPE_INDUSTRY)
    if missing_types:
        raise RuntimeError(f"Module defaults missing for business types: {sorted(missing_types)}")
    unknown = set()
    for mods in _BUSINESS_TYPE_INDUSTRY.values():
        unknown |= set(mods) - set(MODULE_CATALOG)
    unknown |= CORE_MODULES - set(MODULE_CATALOG)
    if unknown:
        raise RuntimeError(f"Unknown module codes in defaults: {sorted(unknown)}")


def defaults_for_business_type(business_type: str | None) -> frozenset[str]:
    code = coerce_business_type(business_type)
    industry = _BUSINESS_TYPE_INDUSTRY.get(code, frozenset())
    return CORE_MODULES | industry


def module_label(module_code: str) -> str:
    return MODULE_CATALOG.get(module_code, module_code)


def list_module_catalog() -> list[dict]:
    return [
        {
            "code": code,
            "label": label,
            "is_core": code in CORE_MODULES,
        }
        for code, label in MODULE_CATALOG.items()
    ]


# Validate at import so misconfigured matrices fail fast in tests/CI.
assert_module_catalog_complete()
