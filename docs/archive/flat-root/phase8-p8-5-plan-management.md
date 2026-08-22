# Sprint P8-5 Completion Report — Plan management

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Subscription plans are **database-backed**, not hardcoded. Master Admin can create, edit, activate, and deactivate plans (features, price, billing cycle, display order, trial eligibility, public flag). Changing a plan price **does not** rewrite `subscriptions.price_at_purchase`. Deactivating a plan does **not** delete existing subscriptions.

## Database changes

| Change | Notes |
|--------|--------|
| `subscription_plans` | Catalog: `name`, `description`, `price` DECIMAL(12,2) ≥ 0, `currency` INR, `billing_cycle` MONTHLY\|YEARLY, `trial_eligible`, `is_public`, `is_active`, `display_order`, `features` JSON |
| `subscriptions.plan_id` | FK → `subscription_plans.id` ON DELETE SET NULL (nullable; trials stay without a plan) |
| `02_schema.sql` | CREATE plans before subscriptions; seed default plan `33333333-3333-3333-3333-333333333333` (₹550 / month) |
| `scripts/apply_subscription_plans.py` | Idempotent; listed in `apply_pending_schema.py` |

**No** tenant/user/bill tables altered. **No** data deleted.

## API changes

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/master/plans` | `master_required`; `include_inactive` default true |
| POST | `/api/v1/master/plans` | Create (201) |
| GET | `/api/v1/master/plans/:id` | Detail |
| PUT | `/api/v1/master/plans/:id` | Partial update; price change does not touch billed snapshots |
| PATCH | `/api/v1/master/plans/:id/status` | `{ "is_active": true\|false }` |

Owner/Billing hitting plan APIs → **403**.  
Empty name or negative price → **400**.  
List ordered by `display_order`, then name.

**Not in this sprint:** public `GET /public/plans` (P8-8).

## Frontend changes

| Path | Change |
|------|--------|
| `/master/plans` | Table + create/edit dialog; features as one-per-line; deactivate confirm |

Landing pricing copy is unchanged until P8-8.

## Tests

`pytest tests/test_p8_5_plan_management.py` plus existing Master/auth suite.

## Known issues / residuals

- Paid subscribe / expiry lockout not built (P8-6).  
- Landing still uses hardcoded ₹550 (P8-8).  
- `expiry_warning_days` unused (P8-7).  
- `is_public` is stored but not served to the public site yet.

---

**Stopped.** Should I start the next sprint? (P8-6 Subscription lifecycle + access gate)
