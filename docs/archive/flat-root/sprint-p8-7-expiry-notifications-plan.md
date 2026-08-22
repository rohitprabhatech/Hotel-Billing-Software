# Sprint Plan — P8-7 Notifications, email, scheduled expiry checks

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- Idempotent subscription expiry notice log keyed by subscription + notice type + entitlement period
- Tenant in-app notices for `SUBSCRIPTION_EXPIRING` and `SUBSCRIPTION_EXPIRED`
- Owner email alerts for expiring and expired subscriptions
- Platform-wide Master Admin notification bell and notification APIs
- CLI job for Windows Task Scheduler / cron so expiry checks do not depend on app traffic
- Configurable `expiry_warning_days` in Master trial settings

## Non-goals

- Public landing plan API (P8-8)
- Payment gateway checkout
- Mixing Master alerts into Owner/Billing dashboards
- In-process APScheduler as the source of truth
