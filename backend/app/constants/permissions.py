"""Tenant role permission matrix (BIZ-03).

Permissions are coarse capabilities checked in services and routes.
Owner receives all permissions; Manager is intentionally restrictive.
"""

from __future__ import annotations

from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER

# Capability codes
PERM_BILLING = "billing"
PERM_REPORTS = "reports"
PERM_STOCK_MOVEMENTS = "stock_movements"
PERM_ITEMS_READ = "items.read"
PERM_ITEMS_WRITE = "items.write"
PERM_ITEMS_STOCK = "items.stock"
PERM_CATEGORIES_READ = "categories.read"
PERM_CATEGORIES_WRITE = "categories.write"
PERM_CUSTOMERS_READ = "customers.read"
PERM_CUSTOMERS_WRITE = "customers.write"
PERM_SUPPLIERS_READ = "suppliers.read"
PERM_SUPPLIERS_WRITE = "suppliers.write"
PERM_PURCHASES_READ = "purchases.read"
PERM_PURCHASES_WRITE = "purchases.write"
PERM_EXPENSES_READ = "expenses.read"
PERM_EXPENSES_WRITE = "expenses.write"
PERM_TABLES_READ = "tables.read"
PERM_TABLES_WRITE = "tables.write"
PERM_TABLES_STATUS = "tables.status"
PERM_ORDERS_READ = "orders.read"
PERM_ORDERS_WRITE = "orders.write"
PERM_KOT_READ = "kot.read"
PERM_KOT_WRITE = "kot.write"
PERM_KOT_STATUS = "kot.status"
PERM_RECIPES_READ = "recipes.read"
PERM_RECIPES_WRITE = "recipes.write"
PERM_ADDONS_READ = "addons.read"
PERM_ADDONS_WRITE = "addons.write"
PERM_WASTAGE_READ = "wastage.read"
PERM_WASTAGE_WRITE = "wastage.write"
PERM_USERS_MANAGE = "users.manage"
PERM_TENANT_SETTINGS = "tenant.settings"
PERM_AUDIT = "audit"
PERM_AI = "ai"
PERM_NOTIFICATIONS = "notifications"

ALL_PERMISSIONS: frozenset[str] = frozenset(
    {
        PERM_BILLING,
        PERM_REPORTS,
        PERM_STOCK_MOVEMENTS,
        PERM_ITEMS_READ,
        PERM_ITEMS_WRITE,
        PERM_ITEMS_STOCK,
        PERM_CATEGORIES_READ,
        PERM_CATEGORIES_WRITE,
        PERM_CUSTOMERS_READ,
        PERM_CUSTOMERS_WRITE,
        PERM_SUPPLIERS_READ,
        PERM_SUPPLIERS_WRITE,
        PERM_PURCHASES_READ,
        PERM_PURCHASES_WRITE,
        PERM_EXPENSES_READ,
        PERM_EXPENSES_WRITE,
        PERM_TABLES_READ,
        PERM_TABLES_WRITE,
        PERM_TABLES_STATUS,
        PERM_ORDERS_READ,
        PERM_ORDERS_WRITE,
        PERM_KOT_READ,
        PERM_KOT_WRITE,
        PERM_KOT_STATUS,
        PERM_RECIPES_READ,
        PERM_RECIPES_WRITE,
        PERM_ADDONS_READ,
        PERM_ADDONS_WRITE,
        PERM_WASTAGE_READ,
        PERM_WASTAGE_WRITE,
        PERM_USERS_MANAGE,
        PERM_TENANT_SETTINGS,
        PERM_AUDIT,
        PERM_AI,
        PERM_NOTIFICATIONS,
    }
)

_MANAGER_PERMISSIONS: frozenset[str] = frozenset(
    {
        PERM_BILLING,
        PERM_REPORTS,
        PERM_STOCK_MOVEMENTS,
        PERM_ITEMS_READ,
        PERM_ITEMS_STOCK,
        PERM_CATEGORIES_READ,
        PERM_CUSTOMERS_READ,
        PERM_CUSTOMERS_WRITE,
        PERM_SUPPLIERS_READ,
        PERM_SUPPLIERS_WRITE,
        PERM_PURCHASES_READ,
        PERM_PURCHASES_WRITE,
        PERM_EXPENSES_READ,
        PERM_EXPENSES_WRITE,
        PERM_TABLES_READ,
        PERM_TABLES_WRITE,
        PERM_TABLES_STATUS,
        PERM_ORDERS_READ,
        PERM_ORDERS_WRITE,
        PERM_KOT_READ,
        PERM_KOT_WRITE,
        PERM_KOT_STATUS,
        PERM_RECIPES_READ,
        PERM_RECIPES_WRITE,
        PERM_ADDONS_READ,
        PERM_ADDONS_WRITE,
        PERM_WASTAGE_READ,
        PERM_WASTAGE_WRITE,
        PERM_NOTIFICATIONS,
    }
)

_BILLING_USER_PERMISSIONS: frozenset[str] = frozenset(
    {
        PERM_BILLING,
        PERM_ITEMS_READ,
        PERM_ITEMS_WRITE,
        PERM_ITEMS_STOCK,
        PERM_CATEGORIES_READ,
        PERM_CUSTOMERS_READ,
        PERM_CUSTOMERS_WRITE,
        PERM_SUPPLIERS_READ,
        PERM_TABLES_READ,
        PERM_TABLES_STATUS,
        PERM_ORDERS_READ,
        PERM_ORDERS_WRITE,
        PERM_KOT_READ,
        PERM_KOT_WRITE,
        PERM_ADDONS_READ,
        PERM_NOTIFICATIONS,
    }
)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    ROLE_OWNER: ALL_PERMISSIONS,
    ROLE_MANAGER: _MANAGER_PERMISSIONS,
    ROLE_BILLING_USER: _BILLING_USER_PERMISSIONS,
}

# Roles an Owner may assign when creating tenant staff (never OWNER or MASTER).
ASSIGNABLE_TENANT_ROLES: frozenset[str] = frozenset({ROLE_BILLING_USER, ROLE_MANAGER})

TENANT_STAFF_ROLES: frozenset[str] = frozenset(
    {ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER}
)


def permissions_for_role(role: str | None) -> frozenset[str]:
    if not role:
        return frozenset()
    return ROLE_PERMISSIONS.get(str(role).upper(), frozenset())


def has_permission(role: str | None, permission: str) -> bool:
    return permission in permissions_for_role(role)


def has_any_permission(role: str | None, *permissions: str) -> bool:
    role_perms = permissions_for_role(role)
    return any(p in role_perms for p in permissions)


def list_permissions_for_role(role: str | None) -> list[str]:
    return sorted(permissions_for_role(role))
