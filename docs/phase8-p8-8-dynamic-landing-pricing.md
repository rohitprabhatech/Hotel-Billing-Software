# Sprint P8-8 Completion Report — Dynamic landing page pricing

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** The public landing page now reads pricing from the API instead of hardcoded copy. Master-created plans marked both **active** and **public** appear automatically on the landing page in `display_order`, with no frontend code edit required.

## API changes

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/public/plans` | Anonymous |

Returned fields are landing-safe only: `id`, `name`, `description`, `price`, `currency`, `billing_cycle`, `trial_eligible`, `display_order`, `features`.

## Backend changes

| Area | Change |
|------|--------|
| `SubscriptionPlanRepository` | Added active+public list query ordered by `display_order` |
| `PlanService` | Added public serialization without internal subscriber counts |
| `public_routes.py` | Anonymous `/public/plans` route |

No tenant-scoped data is exposed. No auth token is required.

## Frontend changes

| Path / component | Change |
|------------------|--------|
| `HomePage` | Fetches public plans on load |
| `HeroSection` | Shows the first live public price as the landing headline |
| `PricingSection` | Renders one or more live public plan cards |
| `SubscriptionPlanInfo` | Accepts an optional plan payload so landing can stay API-driven while Owner UI keeps its existing informational fallback |
| `TermsOfServicePage` | Removed the hardcoded published INR amount from legal copy |

If no public plans are published, the landing now shows a graceful “pricing on request” message instead of a fake stale amount.

## Tests

- `backend/tests/test_p8_8_public_pricing.py`
- `frontend` production build passes
- Full backend regression was started after the targeted P8-8 tests passed

## Known issues / residuals

- Online checkout is still not implemented.
- Landing pricing is informational; activation and renewal remain operator-managed.

---

**Stopped.** Should I start the next sprint? (P8-9 Security + tenant isolation)
