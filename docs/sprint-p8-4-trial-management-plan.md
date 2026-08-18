# Sprint Plan — P8-4 Trial management

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- `platform_settings` singleton: `trial_enabled`, `trial_days` (default 15, not hardcoded)
- `subscriptions` row created on **new** Master approval when trial is ON
- Global ON/OFF and duration changes do **not** rewrite existing trials
- Master Trial settings UI + active trials list + dashboard KPI
- Owner dashboard shows remaining trial days (no access gate yet)

## Non-goals

- Plan CRUD (P8-5)
- Expiry lockout / paid ACTIVE / renewal (P8-6)
- Expiry emails/cron (P8-7)
- Landing price API (P8-8)
- Payment gateway
