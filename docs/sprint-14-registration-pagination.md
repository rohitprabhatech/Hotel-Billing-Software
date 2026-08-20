# Sprint 14 — Master registration-request list pagination

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Wire the Master **Registration requests** page to the existing SQL-paginated list API, and show business names instead of a blank dash.

This sprint does **not**:

- seed a live Master Admin
- migrate or drop hosted data
- change approve / reject behaviour

---

## What changed

`GET /api/v1/master/registration-requests` already paginates in SQL. The UI requested `per_page: 50` and had no pager.

Now:

- `PaginationBar` with `per_page: 25`
- Reloads when status or page changes; Apply / Enter resets to page 1
- `TruncateText` uses `value={row.business_name}` so names render

---

## Tests

| Check | Result |
|-------|--------|
| Two pending requests, `per_page=1` page 1 vs 2 | Distinct rows |
| Owner JWT | 403 |
| P8-3 registration approval | Pass |
| Full backend pytest | **237 passed** |
| Frontend `npm run build` | Green (1667 modules) |

---

## Remaining

- Seed live Master Admin when `MASTER_ADMIN_*` is set
- Other Master lists (plans, audit) may still load a single large page

---

## Stop

Sprint 14 is complete.

Should I start the next sprint?
