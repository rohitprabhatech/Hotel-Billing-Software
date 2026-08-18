# Sprint Plan — P8-2 Master Admin authentication + dashboard foundation

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- `master_admins` table (no `tenant_id`)
- Same `/api/v1/auth/login` issues Master JWT (`role=MASTER_ADMIN`, no `tenant_id`)
- `master_required` vs `auth_required` (403 both directions)
- `/master` shell + live tenant count dashboard
- Seed script from env (no passwords in source)

## Non-goals

- Registration approval, trials, plans, subscriptions, landing price API
- Mixing Master nav into OwnerLayout
- Payment gateway
