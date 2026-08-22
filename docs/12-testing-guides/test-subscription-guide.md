# Test Subscription Guide

_Derived from prior guides; historical originals archived._

# Subscription Management — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Operator UI:** Master → Businesses  
**There is no in-app payment gateway.** Renewals are recorded by Master after offline payment.

---

## Statuses (`subscriptions.status`)

| Status | Owner login | Billing access |
|--------|-------------|----------------|
| `TRIAL` | Yes | Yes |
| `ACTIVE` | Yes | Yes |
| `EXPIRING` | Yes | Yes (warning window) |
| `EXPIRED` | Yes | No (402) |
| `CANCELLED` | Yes | No (402) |
| `SUSPENDED` | Yes | No (402) |

`EXPIRING` is computed from `ends_at` / `trial_ends_at` vs `platform_settings.expiry_warning_days`. Cancelled and suspended statuses are **not** overwritten by the expiry job.

Tenant **deactivation** is separate: `tenants.status = SUSPENDED` blocks **login**. That is not a subscription status.

---

## Fields that matter commercially

| Field | Meaning |
|-------|---------|
| `plan_id` | Current catalog plan (nullable) |
| `price_at_purchase` | Snapshot at assign/renew. Later plan price edits do not change this |
| `payment_status` | `MANUAL` (recorded renewal) or `COMPLIMENTARY` (no end date) |
| `ends_at` | Paid/trial end. `NULL` with complimentary = no expiry |

---

## Master operations

| Action | Effect |
|--------|--------|
| Assign plan | Optional duration days; omit days = complimentary |
| Start / extend trial | Sets/extends trial dates |
| Renew | Adds a paid period from now or from the current future end; snapshots price |
| Cancel subscription | Status CANCELLED; login remains |
| Suspend / Resume | Billing lock without deactivating the tenant |

Existing businesses with no subscription row are grandfathered as complimentary ACTIVE when `apply_subscription_lifecycle.py` runs (idempotent; does not drop data).

---

## Owner view

Owner Settings shows the current plan/status. There is **no Pay button**. Contact Prabha Technology to renew. Expired owners can still open Profile.

Related: [trial-management.md](./trial-management.md) · [plan-management.md](./plan-management.md) · [master-admin-manual.md](./master-admin-manual.md)
