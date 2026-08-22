# Sprint P8-6 Completion Report — Subscription lifecycle + access gate

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Tenant billing APIs now require an entitled subscription. Existing businesses without a row received **complimentary ACTIVE** access (no end date) so they are not locked out. Expired or cancelled businesses can still **sign in** and use profile/password, but cannot bill. Master Admin can assign a plan, extend a trial, record a **manual** renewal, or cancel.

## Database changes

| Change | Notes |
|--------|--------|
| No new tables | Lifecycle uses existing `subscriptions` + `platform_settings.expiry_warning_days` |
| `scripts/apply_subscription_lifecycle.py` | Idempotent grandfather: one complimentary ACTIVE row per tenant that had none |
| Listed in `apply_pending_schema.py` | Run after `apply_subscription_plans.py` |

**No** tenant/user/bill tables altered. **No** data deleted. `tenants.status` is still only ACTIVE/SUSPENDED — expiry lives on `subscriptions`.

## API changes

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/master/businesses` | `status`, `q`, `page`; `EXPIRING` uses warning window |
| GET | `/api/v1/master/businesses/expiring` | Shortcut for expiring-soon |
| GET | `/api/v1/master/businesses/:tenant_id` | Detail + current subscription |
| POST | `/api/v1/master/businesses/:id/assign-plan` | `{ plan_id, days? }` — omit days = complimentary |
| POST | `/api/v1/master/businesses/:id/extend-trial` | `{ days }` (1–365) |
| POST | `/api/v1/master/businesses/:id/renew` | `{ days, plan_id? }` — snapshots `price_at_purchase`; `payment_status=MANUAL` |
| POST | `/api/v1/master/businesses/:id/cancel-subscription` | Status CANCELLED; login still allowed |
| GET | `/api/v1/master/dashboard/summary` | Adds `expiring_soon`, `expired_subscriptions` |

Tenant business APIs (`/bills`, `/items`, …) require TRIAL, ACTIVE, or EXPIRING. Otherwise **402** `SUBSCRIPTION_INACTIVE`.  
Exempt: login/logout/`/auth/me`/change-password, `/profile`.  
Owner hitting Master APIs → **403**. Inactive plans cannot be assigned.

`GET /auth/me` includes `access_allowed`, `is_expiring`, `is_complimentary`.

## Frontend changes

| Path | Change |
|------|--------|
| `/master/businesses` | List + assign / trial / renew / cancel |
| Master dashboard | Expiring soon + expired KPIs |
| Owner / Billing shells | Lockout panel when not entitled; profile still reachable |
| Owner dashboard | Expiring warning (paid) + existing trial banner |

## Tests

`pytest tests/test_p8_6_subscription_lifecycle.py` plus existing Master/auth suite. Seeded tenants are grandfathered in `conftest.py`.

## Known issues / residuals

- Expiry emails and a scheduled job are not built (P8-7). Lazy refresh on request is enough for the access gate.  
- Landing still uses hardcoded ₹550 (P8-8).  
- No payment gateway — renew is operator-recorded only.  
- `subscription SUSPENDED` is in the CHECK but unused.

---

**Stopped.** Should I start the next sprint? (P8-7 Notifications, email, scheduled expiry checks)
