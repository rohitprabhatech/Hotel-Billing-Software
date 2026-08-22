# Tenant Isolation

`tenant_id` comes from JWT/session context only. Cross-tenant access → **403/404**.

Test Users, Customers, Products, Bills, Payments, Purchases, Inventory, Expenses, Reports, Notifications, Audit, Settings.

See [../10-testing/tenant-isolation-testing.md](../10-testing/tenant-isolation-testing.md).
