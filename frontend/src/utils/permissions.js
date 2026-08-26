/** Permission codes returned on /auth/me (BIZ-03). */

export const PERM_BILLING = 'billing';
export const PERM_REPORTS = 'reports';
export const PERM_STOCK_MOVEMENTS = 'stock_movements';
export const PERM_ITEMS_READ = 'items.read';
export const PERM_ITEMS_WRITE = 'items.write';
export const PERM_ITEMS_STOCK = 'items.stock';
export const PERM_CATEGORIES_READ = 'categories.read';
export const PERM_CATEGORIES_WRITE = 'categories.write';
export const PERM_CUSTOMERS_READ = 'customers.read';
export const PERM_CUSTOMERS_WRITE = 'customers.write';
export const PERM_SUPPLIERS_READ = 'suppliers.read';
export const PERM_SUPPLIERS_WRITE = 'suppliers.write';
export const PERM_PURCHASES_READ = 'purchases.read';
export const PERM_PURCHASES_WRITE = 'purchases.write';
export const PERM_EXPENSES_READ = 'expenses.read';
export const PERM_EXPENSES_WRITE = 'expenses.write';
export const PERM_TABLES_READ = 'tables.read';
export const PERM_TABLES_WRITE = 'tables.write';
export const PERM_TABLES_STATUS = 'tables.status';
export const PERM_ORDERS_READ = 'orders.read';
export const PERM_ORDERS_WRITE = 'orders.write';
export const PERM_KOT_READ = 'kot.read';
export const PERM_KOT_WRITE = 'kot.write';
export const PERM_KOT_STATUS = 'kot.status';
export const PERM_RECIPES_READ = 'recipes.read';
export const PERM_RECIPES_WRITE = 'recipes.write';
export const PERM_ADDONS_READ = 'addons.read';
export const PERM_ADDONS_WRITE = 'addons.write';
export const PERM_WASTAGE_READ = 'wastage.read';
export const PERM_WASTAGE_WRITE = 'wastage.write';
export const PERM_PRODUCTION_READ = 'production.read';
export const PERM_PRODUCTION_WRITE = 'production.write';
export const PERM_USERS_MANAGE = 'users.manage';
export const PERM_TENANT_SETTINGS = 'tenant.settings';
export const PERM_AUDIT = 'audit';
export const PERM_AI = 'ai';
export const PERM_NOTIFICATIONS = 'notifications';

export function hasPermission(user, permission) {
  return Array.isArray(user?.permissions) && user.permissions.includes(permission);
}

export function stockMovementsPath(role) {
  return role === 'OWNER' ? '/owner/stock-movements' : '/billing/stock-movements';
}
