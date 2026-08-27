import { useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { hasPermission } from '../utils/permissions';

export function usePermissions() {
  const { user } = useAuth();

  return useMemo(
    () => ({
      user,
      hasPermission: (permission) => hasPermission(user, permission),
      canWriteItems: hasPermission(user, 'items.write'),
      canWriteCategories: hasPermission(user, 'categories.write'),
      canStockItems: hasPermission(user, 'items.stock'),
      canReports: hasPermission(user, 'reports'),
      canStockMovements: hasPermission(user, 'stock_movements'),
      canManageCustomers: hasPermission(user, 'customers.write'),
      canManageSuppliers: hasPermission(user, 'suppliers.write'),
      canViewPurchases: hasPermission(user, 'purchases.read'),
      canManagePurchases: hasPermission(user, 'purchases.write'),
      canViewExpenses: hasPermission(user, 'expenses.read'),
      canManageExpenses: hasPermission(user, 'expenses.write'),
      canViewTables: hasPermission(user, 'tables.read'),
      canManageTables: hasPermission(user, 'tables.write'),
      canUpdateTableStatus: hasPermission(user, 'tables.status'),
      canViewOrders: hasPermission(user, 'orders.read'),
      canManageOrders: hasPermission(user, 'orders.write'),
      canBilling: hasPermission(user, 'billing'),
      canManageRecipes: hasPermission(user, 'recipes.write'),
      canViewRecipes: hasPermission(user, 'recipes.read'),
      canViewAddons: hasPermission(user, 'addons.read'),
      canManageAddons: hasPermission(user, 'addons.write'),
      canFireKot: hasPermission(user, 'kot.write'),
      canViewKitchen: hasPermission(user, 'kot.read'),
      canUpdateKotStatus: hasPermission(user, 'kot.status'),
      canManageKots:
        (user?.role === 'OWNER' || user?.role === 'MANAGER') && hasPermission(user, 'kot.write'),
      canManageUsers: hasPermission(user, 'users.manage'),
      canAudit: hasPermission(user, 'audit'),
    }),
    [user],
  );
}
