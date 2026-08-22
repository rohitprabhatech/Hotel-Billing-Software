# Sprint 9 — Non-destructive live schema apply

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Target:** `u583892242_HotelBillingDB` on `srv1952.hstgr.io`

---

## Scope

Apply missing Phase 8 / SaaS tables to the **existing** hosted database using idempotent helpers only.

This sprint does **not**:

- run `backend/sql/02_schema.sql` (destructive)
- drop tenants, users, bills, or other live rows
- seed a Master Admin password (no `MASTER_ADMIN_*` in `.env`)
- add Alembic revisions

---

## Backup (before writes)

| Field | Value |
|-------|--------|
| Taken at (UTC) | 2026-08-18 11:34:08 |
| Location | `backend/backups/20260818T113408Z-u583892242_HotelBillingDB.json` (gitignored; contains hashes) |
| Verified | tenants=1, users=1, bills=2, bill_items=5, audit_logs=20, items=3, stock_movements=2 — matches Sprint 8 inspect |

New helper: `backend/scripts/backup_database.py` (read-only JSON dump).

---

## Apply

Command: `python scripts/apply_pending_schema.py`

Hosted server is **MariaDB**. Two helpers needed MariaDB-safe SQL:

| Issue | Fix |
|-------|-----|
| `ALTER TABLE … DROP CHECK name` syntax error | `scripts/schema_helpers.py` — try `DROP CONSTRAINT`, then `DROP CHECK`, using savepoints |
| `CAST(:features AS JSON)` syntax error | Seed plan features as a JSON string bind |

**Created (were missing):**

- `master_admins`
- `registration_requests`
- `platform_settings` (singleton: trial 15 days ON)
- `subscriptions`
- `subscription_plans` + default **Business Billing Plan** ₹550 / month
- `subscriptions.plan_id` FK
- complimentary `ACTIVE` subscription for the **1** existing tenant
- `subscription_notices`
- `platform_notifications`
- `platform_audit_logs`

Core billing tables were already present; helpers skipped existing columns/indexes.

---

## Re-inspect (after)

Saved: [`sprint-9-post-apply-inspect.json`](./sprint-9-post-apply-inspect.json)

| Field | Before (Sprint 8) | After |
|-------|-------------------|--------|
| Table count | 15 | **23** |
| Phase 8 tables missing | 8 | **0** |
| tenants / users / bills / bill_items | 1 / 1 / 2 / 5 | **1 / 1 / 2 / 5** (unchanged) |
| subscriptions | — | 1 (complimentary) |
| subscription_plans | — | 1 |
| master_admins | — | **0** (table empty — seed not run) |

---

## Master Admin seed

Skipped. `MASTER_ADMIN_EMAIL` / `MASTER_ADMIN_PASSWORD` are not in `backend/.env`.

When you are ready:

```powershell
cd backend
# set MASTER_ADMIN_EMAIL, MASTER_ADMIN_PASSWORD (min 8), optional MASTER_ADMIN_NAME
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

Do not commit those values.

---

## Tests

| Check | Result |
|-------|--------|
| Backend pytest | **224 passed** |
| Live tenant/bill counts stable | Yes |
| `02_schema.sql` not used | Yes |

---

## Remaining (later sprints)

- Seed the first Master Admin
- Optional Alembic coverage for Phase 8 tables (`alembic_version` still absent)
- Confirm hosted app `.env` uses the same MySQL target
- Final verification / signoff

---

## Stop

Sprint 9 is complete.

Should I start the next sprint?
