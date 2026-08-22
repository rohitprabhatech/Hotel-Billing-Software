# Sprint 15 — Master dashboard KPI filters

**Date:** 2026-08-19  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Let Master Admin open the **right** businesses list from the dashboard. Account (login) and subscription (billing) stay separate filters.

This sprint does **not**:

- seed a live Master Admin
- migrate or drop hosted data
- change activate / deactivate / suspend behaviour

---

## What changed

Dashboard KPIs previously dumped **Expiring** and **Expired** onto an unfiltered businesses page. **Active** / **Suspended** (tenant account) were not clickable.

Now:

| KPI | Opens |
|-----|--------|
| Total businesses | `/master/businesses` |
| Active businesses | `?tenant_status=ACTIVE` |
| Suspended businesses | `?tenant_status=SUSPENDED` (deactivated accounts) |
| Pending requests | Registration queue |
| Trial businesses | Trials |
| Expiring soon | `?status=EXPIRING` |
| Expired subscriptions | `?status=EXPIRED` |

`GET /api/v1/master/businesses` accepts `tenant_status=ACTIVE|SUSPENDED` (SQL-paginated). Combined with `status` it still uses the Sprint 13 ID-filter path.

The businesses UI has an **Account** filter (labeled Deactivated for `SUSPENDED`) and relabels the old Status control as **Subscription**. Changing either updates the URL.

---

## Tests

| Check | Result |
|-------|--------|
| Two deactivated accounts, `per_page=1` page 1 vs 2 | Distinct rows |
| `tenant_status=ACTIVE` excludes deactivated | Pass |
| `tenant_status=ACTIVE&status=TRIAL` | Combined filter |
| `tenant_status=DEACTIVATED` | 400 |
| Owner JWT | 403 |
| Sprint 13 subscription status pagination | Pass |
| Full backend pytest | **241 passed** |
| Frontend `npm run build` | Green (1667 modules) |

---

## Remaining

- Seed live Master Admin when `MASTER_ADMIN_*` is set
- Plans catalog still loads in one page (small table)

---

## Stop

Sprint 15 is complete.

Should I start the next sprint?
