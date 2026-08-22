# Sprint Plan — P8-5 Plan management

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- `subscription_plans` catalog: name, description, price, currency (INR), billing cycle, features, display order, trial eligibility, public flag, active flag
- `subscriptions.plan_id` FK (ON DELETE SET NULL); `price_at_purchase` is a snapshot and is never rewritten when a plan price changes
- Master Admin CRUD + activate/deactivate (UI confirms deactivate)
- Inactive plans are unavailable for new subscriptions; existing rows stay
- Default seed plan: Business Billing Plan ₹550 / month (live MySQL apply)

## Non-goals

- Public landing price API (P8-8) — landing still uses hardcoded copy until then
- Subscription lifecycle / expiry lockout (P8-6)
- Expiry emails/cron (P8-7)
- Payment gateway checkout
- Mixing Master into Owner UI
