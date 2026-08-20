# Sprint 13 — Status-filtered business list pagination

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Stop the Master **status** filter on `/master/businesses` from hydrating every matching tenant row into Python before slicing the page.

This sprint does **not**:

- seed a live Master Admin
- migrate or drop hosted data
- change unfiltered SQL pagination from Sprint 7

---

## What changed

Unfiltered lists were already SQL-paginated (Sprint 7). Status is derived from the **current** subscription after `refresh_status`, so the filter still scans current subscriptions.

Now the status path:

1. Loads matching **tenant IDs** only (`list_ids_matching`)
2. Batch-loads current subscriptions
3. Refreshes status and filters IDs
4. Loads **one page** of tenant rows (`get_many_ordered`)

`meta.total` is the filtered count (not capped at 500).

---

## Tests

| Check | Result |
|-------|--------|
| `status=TRIAL&per_page=1` page 1 vs 2 | Distinct trial businesses |
| `status=ACTIVE` includes Hotel A / Hotel B | Pass |
| Owner JWT | 403 |
| Full backend pytest | **235 passed** |

---

## Remaining

- Seed live Master Admin when `MASTER_ADMIN_*` is set
- EXPIRING still uses derived `is_expiring` (warning window), not a single SQL column

---

## Stop

Sprint 13 is complete.

Should I start the next sprint?
