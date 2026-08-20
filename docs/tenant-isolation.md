# Tenant Isolation — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.

Every registered business is one **tenant**. Data from Business A must never appear for Business B in the UI or API.

---

## How isolation is enforced

1. Business users belong to exactly one `users.tenant_id`.
2. Login puts `tenant_id` in the JWT.
3. Middleware loads the user, checks the tenant is ACTIVE, and sets request context from the **database/JWT**, not from a body field named `tenant_id`.
4. Repositories filter by that context on every tenant-owned table.

Forging `tenant_id` in JSON is ignored.

---

## Tenant-owned data

These rows always carry `tenant_id` (or reach the tenant through a user FK):

- users, categories, items, bills, bill_items, bill_number_counters  
- notifications, audit_logs, stock_movements  
- tenant_whatsapp_configs, bill_deliveries  
- subscriptions, subscription_notices  

Customer name/phone (when collected) live **on the bill**, not in a separate customers table.

---

## Not tenant-owned

| Table | Why |
|-------|-----|
| `roles` | Global OWNER / BILLING_USER |
| `master_admins` | Platform operators |
| `registration_requests` | Queue before a tenant exists |
| `platform_settings` | Singleton trial/warning config |
| `subscription_plans` | Platform catalog |
| `platform_notifications` | Master in-app alerts |
| `platform_audit_logs` | Master actions (optional `tenant_id` link only) |

Master Admin is **not** a tenant. Master JWTs have no `tenant_id`.

---

## Cross-tenant tests (required)

With two businesses (example: **Shree Family Restaurant** and **Smart Fashion Store**):

| Surface | Expected |
|---------|----------|
| Items / categories | A never lists B |
| Bills / print / PDF | A opening B’s id → 404/403 |
| Reports / AI / export | A totals exclude B |
| Owner audit | A never sees B’s LOGIN/CREATE_BILL |
| Notifications | A never sees B’s notices |
| Users | A cannot list B’s staff |
| Subscription on `/auth/me` | A’s entitlement only |

Repeat with **API clients**, not only the browser.

Automated coverage: `test_tenant_isolation.py`, `test_p8_9` notes in [phase8-p8-9-security-isolation.md](./phase8-p8-9-security-isolation.md), reports/audit/AI tests.

---

## Related

- [security-architecture.md](./security-architecture.md)  
- [database-relationships.md](./database-relationships.md)  
- [test-business-billing-guide.md](./test-business-billing-guide.md) Script B and Script I
