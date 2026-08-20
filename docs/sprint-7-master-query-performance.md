# Sprint 7 — Master dashboard query performance

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Stop Master list and dashboard endpoints from loading hundreds of tenants or every historical subscription row into Python.

This sprint does **not**:

- inspect or migrate the live hosted database
- drop tables or reset production data
- add Alembic revisions
- add a payment gateway

---

## Problem

- `list_businesses` loaded tenants with `page=1, per_page=500`, then issued **N+1** `get_current_for_tenant` queries, then filtered and paginated in Python. Tenant 501 never appeared.
- Dashboard `count_expiring` / `count_expired` loaded **all** `Subscription` rows (including historical extras) and walked them in Python. Summary called both, so the table was scanned twice.

---

## What changed

| Area | Change |
|------|--------|
| Current subscription | `SubscriptionRepository.map_current_for_tenants` — chunked `IN` (500), `joinedload` plan+tenant, latest by `created_at.desc(), id.desc()` |
| Unfiltered business list | True SQL pagination via `TenantRepository.list_all`, then batch-load current subscriptions for **that page only** |
| Status filter | `TenantRepository.list_matching` (no 500 cap) + batch current + filter in Python + slice the page (status is derived, not a single SQL column) |
| Dashboard | `SubscriptionService.access_counts()` uses current-per-tenant only; `MasterDashboardService.summary()` calls it **once** |
| Trials list | Eager-load tenant+plan; UI paginates |
| Frontend | `/master/businesses` and `/master/trials` use `PaginationBar` (25 per page); Trials `TruncateText` now uses `value=` so names render |

---

## Tests

| Check | Result |
|-------|--------|
| Backend pytest | **217 passed** |
| Frontend production build | **green** (1667 modules) |
| `GET /master/businesses?page=1&per_page=1` vs page 2 | Distinct rows; `meta.total` is not capped at 500 |
| Seed Hotel A / Hotel B still listed | Pass |
| Dashboard `expiring_soon` / `expired_subscriptions` | Present; still based on current subscription per tenant |
| Owner JWT on Master businesses | 403 |

---

## Changed files (high level)

**Backend**

- `app/repositories/tenant_repository.py` — `list_matching()`, `list_ids()`
- `app/repositories/subscription_repository.py` — `map_current_for_tenants()`, stable current-sub order, trial `joinedload`
- `app/services/subscription_service.py` — rewritten `list_businesses`, `_business_payloads`, `access_counts`
- `app/services/master_dashboard_service.py` — single `access_counts` call
- `tests/test_sprint7_master_query_performance.py` — new

**Frontend**

- `pages/master/MasterBusinessesPage.jsx`
- `pages/master/MasterTrialsPage.jsx`

**Docs**

- this report, `docs/README.md`, `docs/development-roadmap.md`, `docs/master-admin-manual.md`

---

## Remaining (later sprints)

- Live inspect + non-destructive apply when `DATABASE_URL` is available
- Optional: Alembic coverage for Phase 8 tables
- Status-filtered business list still loads matching tenants then slices in Python (unfiltered path is SQL-paginated)
- Final verification / signoff after cloud schema is confirmed

---

## Stop

Sprint 7 is complete.

Should I start the next sprint?
