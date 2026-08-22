# Authorization — Prabha Billing SaaS V2

## Model

RBAC + optional permission overrides + **module entitlement** from BusinessType / plan.

## Business roles (target)

| Role | Intent |
|------|--------|
| OWNER | Full tenant control |
| BILLING_USER | POS / billing; item edits if permitted |
| MANAGER | Mid-tier ops (reports, limited settings) — **new** |

Industry roles (waiter, kitchen) only when restaurant pack needs them.

## Platform role

`MASTER_ADMIN` — separate table; Master APIs only.

## Guards (current → keep)

| Guard | Use |
|-------|-----|
| `auth_required` | Tenant APIs |
| `master_required` | `/master/*` |
| Role allow-lists | Owner-only resources |
| Subscription gate | 402 when billing locked |

## Permission examples

`item.create`, `item.update`, `item.deactivate`, `bill.create`, `bill.cancel`, `report.view`, `user.manage`, …

Owner always sees **item activity / audit** even if billing users mutate catalog.

## Frontend

Route guards are UX only; API enforces truth.
