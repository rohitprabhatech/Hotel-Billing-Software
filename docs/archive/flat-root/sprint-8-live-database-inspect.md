# Sprint 8 — Live database inspect (MYSQL_* connection)

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Connection wiring + **read-only** live inspect. No schema writes.  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Inspect the existing hosted database `u583892242_HotelBillingDB` without creating a new database, dropping tables, or applying helpers.

This sprint does **not**:

- run `apply_pending_schema.py` (backup not recorded in this workspace)
- run `02_schema.sql`
- seed Master Admin
- add Alembic revisions

---

## Why inspect was blocked before

`backend/.env` already had split MySQL fields (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`) but **no** `DATABASE_URL`.

Inspect/apply scripts and Flask config only read `DATABASE_URL`, so they treated the workspace as disconnected.

---

## What changed

| Area | Change |
|------|--------|
| `app/utils/database_url.py` | New. `DATABASE_URL` wins; otherwise builds `mysql+pymysql://…` from `MYSQL_*` (password URL-encoded) |
| Flask `settings.py` | `SQLALCHEMY_DATABASE_URI` uses the resolver (tests still force SQLite via `TestingConfig`) |
| `inspect_database_schema.py` | Loads `backend/.env`; accepts `MYSQL_*`; report includes redacted `target.host` / `database` (no password) |
| `apply_pending_schema.py` | Same resolver; exports `DATABASE_URL` so child helpers still work |
| `.env.example` / SQL README / backup runbook | Document the `MYSQL_*` alternative |

No production data was modified.

---

## Live inspect result (read-only)

Saved: [`sprint-8-live-schema-inspect.json`](./sprint-8-live-schema-inspect.json)

| Field | Value |
|-------|--------|
| Host | `srv1952.hstgr.io` |
| Database | `u583892242_HotelBillingDB` |
| Dialect | mysql |
| Table count | **15** (core billing set complete) |
| Phase 8 SaaS tables present | **none** |
| `alembic_version` | **absent** |

**Missing (must be created later with helpers, not `02_schema.sql`):**

- `master_admins`
- `registration_requests`
- `platform_settings`
- `subscription_plans`
- `subscriptions`
- `subscription_notices`
- `platform_notifications`
- `platform_audit_logs`

**Row counts (spot-check — data exists, do not drop):**

| Table | Rows |
|-------|------|
| tenants | 1 |
| users | 1 |
| items | 3 |
| bills | 2 |
| bill_items | 5 |
| audit_logs | 20 |
| stock_movements | 2 |
| notifications | 0 |

Core columns expected by the current app are already on the live DB (`tenants.business_type`, `users.token_version`, `categories.parent_key`, `items.sku` / `cost_price` / `created_by`, `bills.payment_method`). The gap is **only** the Master/SaaS control-plane tables.

This matches the Sprint 2 upgrade plan.

---

## Tests

| Check | Result |
|-------|--------|
| `tests/test_sprint8_database_url.py` | **4 passed** |
| Full backend pytest | **221 passed** |
| Live inspect | Connected; JSON saved; no writes |
| Schema helpers applied | **No** |

---

## Next sprint (not started)

1. Operator records a **verified backup** (host panel dump or `mysqldump`) of `u583892242_HotelBillingDB`.
2. Then run `python scripts/apply_pending_schema.py` (CREATE-if-missing helpers + complimentary subscription backfill for the existing tenant).
3. Re-inspect; seed Master Admin if `master_admins` is empty.

Do not start that apply until the backup location and timestamp are known.

---

## Stop

Sprint 8 is complete.

Should I start the next sprint?
