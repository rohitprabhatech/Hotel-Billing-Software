# Sprint P8-4 Completion Report — Trial management

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Free trial is **database-configured**, not hardcoded. Default is **ON / 15 days**. Master Admin can turn the trial off or change duration. **New approvals** pick up the current settings; **existing trials are not rewritten**. Seeded businesses have no subscription row (grandfathered until P8-6).

## Database changes

| Change | Notes |
|--------|--------|
| `platform_settings` | Singleton `00000000-0000-0000-0000-000000000001`; `trial_enabled`, `trial_days` (1–365), `expiry_warning_days` (stored, unused until P8-7) |
| `subscriptions` | `tenant_id` FK; `plan_id` nullable (plans in P8-5); trial/period timestamps; `price_at_purchase`; nullable payment fields |
| `02_schema.sql` | CREATE + DROP |
| `scripts/apply_trial_management.py` | Idempotent; listed in `apply_pending_schema.py` |

**No** tenant/user/bill tables altered. **No** data deleted. `tenants.status` stays `ACTIVE` \| `SUSPENDED` — trial lives on `subscriptions`.

## API changes

| Method | Path | Auth |
|--------|------|------|
| GET/PUT | `/api/v1/master/settings/trial` | `master_required` |
| GET | `/api/v1/master/trials` | `master_required` |
| GET | `/api/v1/master/dashboard/summary` | Adds `trial_businesses` |
| POST | `/api/v1/master/registration-requests/:id/approve` | Starts TRIAL when enabled; `data.subscription` |
| GET | `/api/v1/auth/me` | `user.tenant.subscription` (or `null`) |

Owner/Billing hitting trial APIs → **403**.  
`trial_days` 0 or >365 → **400**.  
Trial OFF on approve → `subscription: null` (login still allowed; access gate is P8-6).

Also fixed: `_bind_identity` now clears the other Flask `g` context so a Master call cannot leak into a later Owner `/auth/me` in the same app context (pytest shares one `app_context`).

## Frontend changes

| Path | Change |
|------|--------|
| `/master/settings/trial` | ON/OFF + duration + save |
| `/master/trials` | Active trial list |
| Master dashboard | Trial businesses KPI |
| Owner dashboard | Remaining-days banner when `status=TRIAL` |

Owner/Billing nav otherwise unchanged.

## Tests

`pytest tests/test_p8_4_trial_management.py` plus existing auth/registration suite.

## Known issues / residuals

- Expired trials are **not** locked out yet (P8-6).  
- Plans / paid subscriptions / landing prices not built (P8-5, P8-6, P8-8).  
- `expiry_warning_days` is stored but not used (P8-7).  
- `plan_id` has no FK until `subscription_plans` exists.

---

**Stopped.** Should I start the next sprint? (P8-5 Plan management)
