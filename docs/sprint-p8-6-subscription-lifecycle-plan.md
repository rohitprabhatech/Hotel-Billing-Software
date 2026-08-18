# Sprint Plan — P8-6 Subscription lifecycle + access gate

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- Subscription statuses: TRIAL, ACTIVE, EXPIRING, EXPIRED, CANCELLED (SUSPENDED reserved)
- Lazy expiry on tenant API requests (no cron yet — P8-7)
- Access gate: expired / cancelled / missing subscription → HTTP 402 on business APIs
- Login, `/auth/me`, profile, and password change remain available
- Grandfather existing tenants with complimentary ACTIVE (no end date) **before** enforcing the gate
- Master businesses: assign plan, extend trial, manual renew (price snapshot), cancel
- Expiring-soon uses `platform_settings.expiry_warning_days` (default 5)

## Non-goals

- Payment gateway checkout (renew is a Master-recorded stub)
- Scheduled expiry job / expiry emails (P8-7)
- Public landing plan API (P8-8)
- Mixing Master into Owner UI
