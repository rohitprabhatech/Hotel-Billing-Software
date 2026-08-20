# Backup and Recovery — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Hosted database name (current production target):** `u583892242_HotelBillingDB`

This is the operational runbook for schema changes on the **existing** cloud database. It does not replace your host’s backup product.

---

## Hard rules

- Do **not** create a second unrelated production database for this product.
- Do **not** run `backend/sql/02_schema.sql` on cloud/production (it `DROP TABLE`s).
- Do **not** drop tenants, users, bills, items, stock, or audit to “fix” schema.
- Do **not** apply helpers until a **verified backup** exists and a **read-only inspection** report is saved.

---

## Official upgrade path (existing DB)

1. **Backup** the live MySQL schema + data (host panel dump or `mysqldump`). Store location, timestamp, and who took it.
2. **Inspect** (read-only):

```powershell
cd backend
# DATABASE_URL, or MYSQL_HOST / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE in .env
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out schema-report.json
```

Confirm Phase 8 tables present vs missing (`master_admins`, `registration_requests`, `platform_settings`, `subscription_plans`, `subscriptions`, `subscription_notices`, `platform_notifications`, `platform_audit_logs`).

3. **Apply** idempotent helpers only:

```powershell
.\.venv\Scripts\python.exe scripts\apply_pending_schema.py
```

Helpers **CREATE IF missing**. Hosted MySQL at Hostinger is **MariaDB**: CHECK drops use `DROP CONSTRAINT` (see `scripts/schema_helpers.py`); plan features are inserted as JSON text, not `CAST(... AS JSON)`.

`apply_subscription_lifecycle.py` may **insert** complimentary ACTIVE rows for tenants that have no subscription — that is not a drop.

4. **Re-inspect** and spot-check row counts for `tenants`, `users`, `bills`, `bill_items`.
5. Stamp Alembic if not already set: `python scripts/stamp_alembic_head.py` (`20260818_phase8_saas`).
6. Check readiness, then seed Master Admin if `master_admins` is empty:

```powershell
.\.venv\Scripts\python.exe scripts\check_platform_ready.py
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

Run the seed with **`python.exe`**. A bare `scripts\seed_master_admin.py` may exit without creating a row.

Alembic note: Do **not** `flask db upgrade` from an empty `alembic_version` on a live database. The Phase 8 revision is idempotent CREATE-if-missing; its downgrade does not drop tables.

---

## Fresh local / empty DB only

`01_create_database.sql` + `02_schema.sql` (or `sql/apply_schema.py`). Never use this pair on a database that already has live tenants.

---

## Rollback

| Situation | Action |
|-----------|--------|
| Helper failed mid-run | Restore from the backup taken in step 1. Re-inspect. Re-run helpers (they skip existing tables). |
| Wrong database targeted | Restore that instance from backup. Confirm `DATABASE_URL` database name before retry. |
| Need to undo a complimentary insert | Do not drop `subscriptions`. Correct individual rows via Master UI or a reviewed SQL UPDATE after backup. |

There is no supported “reset production” script.

---

## Record for each production change

| Field | Value |
|-------|--------|
| Backup location | `backend/backups/20260818T113408Z-u583892242_HotelBillingDB.json` (gitignored) |
| Backup timestamp | 2026-08-18 11:34:08 UTC |
| Inspector JSON path | `docs/sprint-8-live-schema-inspect.json` (before), `docs/sprint-9-post-apply-inspect.json` (after) |
| `alembic_version` (if table exists) | `20260818_phase8_saas` (Sprint 11 stamp) |
| Helpers applied | `apply_pending_schema.py` (Sprint 9) |
| Row counts tenants / users / bills (before → after) | 1 / 1 / 2 → 1 / 1 / 2 |
| Operator | Sprint 9 apply |

Related: [deployment-guide.md](./deployment-guide.md) · [sprint-2-cloud-schema-diff-and-upgrade-plan.md](./sprint-2-cloud-schema-diff-and-upgrade-plan.md) · `backend/sql/README.md`
