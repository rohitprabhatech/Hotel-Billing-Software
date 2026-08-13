# 06 — User Roles & Permissions

## Roles (Exactly Two)

| Role Code | Display Name | Purpose |
|-----------|--------------|---------|
| `OWNER` | Hotel Owner | Full tenant management & visibility |
| `BILLING_USER` | Billing User | Day-to-day billing operations |

No Manager, Admin User, Accountant, or Supervisor in this version.

## Hierarchy

```text
Hotel Owner
    └── Billing User(s)
```

## Permission Matrix

Legend: ✅ Allow · ❌ Deny · ◐ Limited

| Capability | OWNER | BILLING_USER |
|------------|:-----:|:------------:|
| Login / Logout | ✅ | ✅ |
| View owner dashboard analytics | ✅ | ❌ |
| View billing dashboard (simple) | ◐ optional | ✅ |
| Create / finalize bill | ✅ | ✅ |
| Draft: add/remove/qty/discount | ✅ | ✅ |
| Print / reprint bill | ✅ | ✅ (if permitted) |
| Cancel / void bill (with reason) | ✅ | ✅ (policy: allow with audit) |
| Hard delete bill / bill items | ❌ | ❌ |
| View all tenant bills | ✅ | ◐ today's / own / recent as designed |
| Manage categories | ✅ | ❌ |
| Manage items / prices / GST on items | ✅ | ❌ |
| Activate / deactivate items | ✅ | ❌ |
| Manage billing users | ✅ | ❌ |
| Update tenant profile (GSTIN, FSSAI, address) | ✅ | ❌ |
| View audit logs | ✅ | ❌ |
| Delete audit logs | ❌ | ❌ |
| Export sales reports | ✅ | ❌ |
| View fraud/activity alerts | ✅ | ❌ |
| Access other tenants | ❌ | ❌ |

## Endpoint Authorization Summary

| Area | OWNER | BILLING_USER |
|------|-------|--------------|
| `/api/v1/auth/*` | login/logout/me | login/logout/me |
| `/api/v1/tenants` (own profile) | read/update | read limited (for receipt header via bill APIs) |
| `/api/v1/users` | CRUD for billing users | ❌ |
| `/api/v1/categories` | full | list active |
| `/api/v1/items` | full | list/search active |
| `/api/v1/bills` | full (incl. cancel) | create, list scoped, get, cancel, print audit hooks |
| `/api/v1/reports/*` | ✅ | ❌ |
| `/api/v1/audit-logs/*` | ✅ | ❌ |

## Billing User Restrictions (Critical)

Billing User **must not**:

- Access owner analytics or audit dashboard APIs
- Manage users or tenant settings
- Permanently delete historical financial records
- See or export other tenants' data
- Delete audit logs
- Perform direct DB operations through the app

## Cancel Bill Policy

Both roles may cancel a finalized bill **via status transition** with mandatory reason. Original bill remains; audit captures actor, time, reason, amounts.

Future versions may restrict cancel to OWNER only; v1 allows Billing User cancel with strong audit (owner visibility).

## Frontend Route Guards

| Route group | Allowed roles |
|-------------|---------------|
| `/owner/*` | OWNER |
| `/billing/*` | BILLING_USER (OWNER may access billing screen optionally) |
| `/login` | Public |
| `/print/bills/:id` | Authenticated + can view bill |

Backend remains source of truth; frontend guards are UX only.
