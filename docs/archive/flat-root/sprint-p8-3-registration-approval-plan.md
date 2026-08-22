# Sprint Plan — P8-3 Business registration approval

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- Public register creates a **PENDING** `registration_requests` row (no tenant, no login)
- Terms of Service / Privacy Policy checkbox required
- Master Admin list / view / approve / reject (reject requires reason)
- Approve creates ACTIVE tenant + OWNER (`email_verified=True`)
- Grandfather existing ACTIVE tenants
- Received / approved / rejected emails

## Non-goals

- Trial dates, plans, subscriptions, landing price API
- Payment gateway
- Mixing Master into Owner UI
- Changing `tenants.status` CHECK to include PENDING
