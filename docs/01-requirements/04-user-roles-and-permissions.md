# User Roles and Permissions

# 06 — User Roles & Permissions

## Roles (Three Tenant Roles)

| Role Code | Display Name | Purpose |
|-----------|--------------|---------|
| `OWNER` | Business Owner | Full tenant management & visibility |
| `MANAGER` | Manager | Operations — billing, reports, stock (no admin settings) |
| `BILLING_USER` | Billing User | Day-to-day billing and catalog updates at counter |

Platform also has `MASTER_ADMIN` (Prabha Technology) — not a tenant role.

## Hierarchy

```text
Business Owner
    ├── Manager(s)        ← ops + reports + stock
    └── Billing User(s)   ← counter billing
```

## Permission Matrix (BIZ-03)

Legend: ✅ Allow · ❌ Deny · ◐ Limited

| Capability | OWNER | MANAGER | BILLING_USER |
|------------|:-----:|:-------:|:------------:|
| Login / Logout | ✅ | ✅ | ✅ |
| View owner dashboard analytics | ✅ | ❌ | ❌ |
| View billing dashboard | ◐ | ✅ | ✅ |
| Create / finalize bill | ✅ | ✅ | ✅ |
| Print / reprint bill | ✅ | ✅ | ✅ |
| Cancel bill (with reason) | ✅ | ✅ | ✅ |
| View sales reports / export | ✅ | ✅ | ❌ |
| View stock movement ledger | ✅ | ✅ | ❌ |
| List / search items | ✅ | ✅ | ✅ |
| Create / edit / deactivate items | ✅ | ❌ | ✅ |
| Adjust / receive stock | ✅ | ✅ | ✅ |
| Manage categories (CRUD) | ✅ | ❌ | ❌ |
| List active categories | ✅ | ✅ | ✅ |
| Manage customers (CRM) | ✅ | ✅ | ✅ |
| Customer credit / udhari | ✅ | ✅ | ✅ collect |
| Manage suppliers | ✅ | ✅ | ◐ read |
| Record purchases (PO / stock in) | ✅ | ✅ | ❌ |
| Manage expenses | ✅ | ✅ | ❌ |
| Manage tenant users | ✅ | ❌ | ❌ |
| Update tenant settings | ✅ | ❌ | ❌ |
| View audit logs / AI assistant | ✅ | ❌ | ❌ |
| Access other tenants | ❌ | ❌ | ❌ |

Permissions are returned on `/api/v1/auth/me` as `permissions[]` and enforced in API services/routes.

## Endpoint Authorization Summary

| Area | OWNER | MANAGER | BILLING_USER |
|------|-------|---------|--------------|
| `/api/v1/auth/*` | login/logout/me | login/logout/me | login/logout/me |
| `/api/v1/tenants/me` | read/update | read | read |
| `/api/v1/users` | CRUD staff | ❌ | ❌ |
| `/api/v1/categories` | full | list active | list active |
| `/api/v1/items` | full | read + stock ops | full catalog ops |
| `/api/v1/customers` | full | full | full on bill / CRM |
| `/api/v1/customers/:id/ledger` | read | read | read |
| `/api/v1/customers/:id/payments` | write | write | write |
| `/api/v1/suppliers` | full | full | read |
| `/api/v1/purchases` | full | full | ❌ |
| `/api/v1/expenses` | full | full | ❌ |
| `/api/v1/bills` | full | full billing | full billing |
| `/api/v1/reports/*` | ✅ | ✅ | ❌ |
| `/api/v1/stock-movements/*` | ✅ | ✅ | ❌ |
| `/api/v1/audit-logs/*` | ✅ | ❌ | ❌ |
| `/api/v1/ai/*` | ✅ | ❌ | ❌ |

## Staff Creation

Owner may create users with role `BILLING_USER` or `MANAGER` only. Owner accounts are created at registration approval.

## Billing User Restrictions (Critical)

Billing User **must not**:

- Access owner analytics, reports, or audit dashboard APIs
- Manage users or tenant settings
- See or export other tenants' data
- Delete audit logs

## Manager Restrictions (Critical)

Manager **must not**:

- Manage users or tenant settings
- Create/edit catalog items or categories
- Access audit logs or AI assistant
- Escalate to Master Admin

## Cancel Bill Policy

Owner, Manager, and Billing User may cancel a finalized bill **via status transition** with mandatory reason. Original bill remains; audit captures actor, time, reason, amounts.

## Frontend Route Guards

| Route group | Allowed roles |
|-------------|---------------|
| `/owner/*` | OWNER |
| `/billing/*` | BILLING_USER, MANAGER (OWNER may access billing optionally) |
| `/billing/reports`, `/billing/stock-movements` | MANAGER (OWNER uses `/owner/*` equivalents) |
| `/master/*` | MASTER_ADMIN |
| `/login` | Public |
| `/print/bills/:id` | Authenticated + can view bill |

Backend remains source of truth; frontend guards and `permissions[]` drive UX hiding.
