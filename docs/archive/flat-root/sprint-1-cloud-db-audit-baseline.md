# Sprint 1 — Cloud DB Audit + Migration Baseline

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Read-only audit only; no schema or application changes applied  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Sprint 1 was limited to:

- verify how the project currently manages schema changes
- determine whether this workspace can access the real configured database
- baseline the current SQLAlchemy models, SQL schema files, and migration path
- identify blockers before any cloud migration or production-safe schema change

No database writes, migrations, or app feature changes were performed.

---

## Executive summary

The application already contains the Phase 8 SaaS architecture in code:

- `master_admins`
- `registration_requests`
- `platform_settings`
- `subscription_plans`
- `subscriptions`
- `subscription_notices`
- `platform_notifications`

However, the production migration story is currently split:

1. older schema changes are tracked in **Alembic / Flask-Migrate**
2. newer SaaS/master schema changes are applied via **idempotent Python helper scripts**

That means the repository currently has **three schema representations**:

- SQLAlchemy models
- `backend/sql/02_schema.sql`
- Alembic revisions + `backend/scripts/apply_pending_schema.py`

The first two are broadly aligned. The migration history is **not** fully aligned because Alembic does not contain Phase 8 table creation revisions.

---

## Database access result

### Workspace database access

- `DATABASE_URL` in the active shell environment: **not set**
- checked-in `backend/.env`: **not present in workspace**
- backend config fallback points to a local placeholder MySQL URL

### Read-only live schema probe

A safe SQLAlchemy inspector connection was attempted through the app configuration. It failed with:

- `Access denied for user 'root'@'localhost'`

### Conclusion

This workspace does **not** currently have usable access to the real cloud database.

Because of that, Sprint 1 could **not** complete these truthfully:

- compare models vs actual live cloud schema
- read `alembic_version` from the deployed database
- verify existing production tables, indexes, constraints, and records
- validate whether helper scripts were already applied in cloud

This is a hard blocker for any safe production migration work.

---

## Current migration baseline

### Alembic present

The project uses Flask-Migrate / Alembic:

- `backend/app/extensions/__init__.py`
- `backend/migrations/env.py`
- `backend/migrations/alembic.ini`

### Alembic revisions currently present

Current checked-in revisions cover earlier generations only, including:

- SaaS auth tokens / user auth fields
- item `created_by`
- bill payment method
- tenant `business_type`
- schema relationship fixes
- item catalog fields
- category parent key
- bill report index
- stock notifications
- WhatsApp bill delivery
- users email uniqueness
- WhatsApp webhook statuses

### Missing from Alembic

No Alembic revisions were found for these Phase 8 structures:

- `master_admins`
- `registration_requests`
- `platform_settings`
- `subscription_plans`
- `subscriptions`
- `subscription_notices`
- `platform_notifications`

### Current authoritative upgrade path

The repo currently documents `backend/scripts/apply_pending_schema.py` as the authoritative upgrade path for existing databases.

Phase 8 helper scripts currently include:

- `apply_master_admins.py`
- `apply_registration_requests.py`
- `apply_trial_management.py`
- `apply_subscription_plans.py`
- `apply_subscription_lifecycle.py`
- `apply_expiry_notifications.py`

---

## Schema representation audit

### SQLAlchemy models

Phase 8 tables are present in `backend/app/models/` and imported in `backend/app/models/__init__.py`.

Key architectural choices already implemented:

- separate `master_admins` table, not tenant-scoped
- tenant-scoped `users`
- `registration_requests` linked back to `master_admins` and optional `tenant_id`
- singleton `platform_settings`
- database-driven `subscription_plans`
- `subscriptions.price_at_purchase` snapshot
- separate tenant notifications and platform notifications
- idempotency table for expiry notices

### `backend/sql/02_schema.sql`

`02_schema.sql` includes the current Phase 8 tables and constraints.

Important note:

- it is valid as a **fresh install / greenfield schema**
- it is **not** valid as a production migration procedure because it starts with `DROP TABLE IF EXISTS ...`

### Documentation and ops guidance

Current docs already acknowledge the split migration path:

- `docs/deployment-guide.md`
- `backend/sql/README.md`
- `docs/database-design.md`
- `docs/database-relationships.md`

Those docs consistently point existing databases to `apply_pending_schema.py`.

---

## Risks identified

1. **No verified cloud DB access in this workspace**  
   Production schema state is unknown from here.

2. **Split migration system**  
   Alembic and helper scripts are both in use, but only helper scripts cover the Phase 8 SaaS tables.

3. **Potential deployment drift**  
   A cloud DB may have some helper-script changes but no matching Alembic history.

4. **Unsafe misuse of `02_schema.sql`**  
   It must never be used on an existing production database.

5. **Unverified backup procedure**  
   No backup artifact, backup timestamp, or rollback procedure is available from this workspace yet.

---

## Required inputs before Sprint 2

Before any real migration implementation or cloud update, one of the following is required:

1. valid read-only access to the real cloud DB from this workspace, or
2. a schema export from the live DB, such as:
   - `SHOW CREATE TABLE` output
   - `mysqldump --no-data`
   - `alembic_version` contents
   - table/index/constraint inventory
3. backup and recovery confirmation for the target cloud database

Without one of those, future migration work would be guesswork.

---

## Recommended Sprint 2 scope

Only after cloud DB access or schema export is available:

- capture deployed schema inventory
- compare live DB against:
  - SQLAlchemy models
  - `02_schema.sql`
  - Alembic history
  - helper-script expectations
- identify exact diffs
- decide whether to:
  - continue using helper scripts as the operational production path, or
  - normalize Phase 8 into Alembic revisions for future upgrades
- document backup, migration version, and rollback steps before any write operation

---

## Changed files in Sprint 1

- `docs/sprint-1-cloud-db-audit-baseline.md` — new audit report

---

## Acceptance status

| Criterion | Result |
|-----------|--------|
| Project schema management audited | Yes |
| SQLAlchemy / SQL schema / migration path compared in repo | Yes |
| Live DB access verified from workspace | No — blocked |
| Cloud schema diff captured | No — blocked by missing access |
| No destructive changes performed | Yes |

---

**Stopped.** Sprint 1 completed as a baseline audit with a cloud-access blocker clearly identified.
