# Sprint 3 — Live DB Inspection Tooling

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Safe tooling + documentation only  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Sprint 3 was limited to one goal:

- add a **read-only inspection tool** that can be pointed at the existing hosted database before any migration or schema upgrade is attempted

No migration was executed. No production data was modified.

---

## What was added

### New script

- `backend/scripts/inspect_database_schema.py`

Purpose:

- inspect the database referenced by `DATABASE_URL`
- confirm whether Phase 8 tables exist already
- capture `alembic_version` if present
- report row counts for key tables
- inspect columns, primary keys, indexes, and foreign keys for core and Phase 8 tables

### Updated ops guide

- `backend/sql/README.md`

Added a new **Inspect first (read-only, recommended)** step before any upgrade.

---

## Script behavior

The inspection script is **read-only**. It does not create, alter, drop, update, or delete any rows or tables.

It reports:

- all discovered tables
- core-table presence
- Phase 8 table presence / missing list
- `alembic_version` table presence
- migration version values if available
- row counts for important tables
- per-table details:
  - columns
  - primary key columns
  - indexes
  - foreign keys

Optional output:

- JSON to stdout
- JSON file via `--json-out`

---

## How to run

```powershell
cd backend
set DATABASE_URL=mysql+pymysql://<user>:<pass>@<host>/u583892242_HotelBillingDB
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out schema-report.json
```

This should be run **before**:

- `apply_pending_schema.py`
- any individual `apply_*.py` helper
- any attempt to normalize the DB into Alembic revisions

---

## Why this sprint matters

Previous sprints established two facts:

1. the original cloud-create SQL is missing Phase 8 Master/SaaS tables
2. we still do not know whether the hosted database was later upgraded by helper scripts

This new tool closes that gap operationally:

- it gives a safe first step for inspecting the real hosted schema
- it helps prevent duplicate table creation attempts
- it provides a machine-readable baseline before any write operation

---

## Verification performed

The script was checked locally in a read-only way:

- import smoke test: **passed**
- execution without `DATABASE_URL`: correctly exits with `DATABASE_URL is required`

No real database connection was attempted in this sprint because valid hosted DB credentials were still not available in the workspace environment.

---

## Changed files

- `backend/scripts/inspect_database_schema.py` — new read-only DB inspection utility
- `backend/sql/README.md` — added inspection-first workflow

---

## Acceptance status

| Criterion | Result |
|-----------|--------|
| Read-only live DB inspection script added | Yes |
| Safe pre-upgrade workflow documented | Yes |
| Script smoke-tested locally | Yes |
| Production database modified | No |

---

**Stopped.** Sprint 3 completed with safe inspection tooling in place.
