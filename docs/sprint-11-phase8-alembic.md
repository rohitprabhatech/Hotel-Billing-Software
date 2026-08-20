# Sprint 11 — Phase 8 Alembic coverage

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Add Alembic coverage for the Master/SaaS tables already created on the hosted database by Sprint 9 helpers.

This sprint does **not**:

- drop tables or tenant data
- run `02_schema.sql`
- seed a Master Admin password (`MASTER_ADMIN_*` still unset)
- replay `flask db upgrade` from an empty version table on live data

---

## Revision

| Field | Value |
|-------|--------|
| File | `backend/migrations/versions/20260818_phase8_saas.py` |
| Revision | `20260818_phase8_saas` |
| Parent | `20260814_wa_webhook_status` |
| Upgrade | CREATE tables if missing; seed settings singleton + default plan if empty; add `fk_subscriptions_plan` if missing |
| Downgrade | **no-op** (never DROP SaaS tables) |

Live databases that already used `apply_pending_schema.py` must **stamp**, not upgrade from zero.

---

## Live stamp

Command: `python scripts/stamp_alembic_head.py`

Refuses SQLite and refuses a Flask URI that does not match `MYSQL_*` / `DATABASE_URL`.

| Field | Value |
|-------|--------|
| Target | `srv1952.hstgr.io` / `u583892242_HotelBillingDB` |
| Result | `alembic_version=['20260818_phase8_saas']` |
| Dialect | MySQLImpl (MariaDB) |
| Tables dropped | none |

---

## Tests

| Check | Result |
|-------|--------|
| `tests/test_sprint11_phase8_alembic.py` | Pass (3) |
| `flask db heads` (testing env) | `20260818_phase8_saas (head)` |
| Full backend pytest | **231 passed** |

---

## Remaining (later sprints)

- Set `MASTER_ADMIN_*` and run `seed_master_admin.py`
- Final verification / signoff after the first Master can sign in at `/master/login`

---

## Stop

Sprint 11 is complete.

Should I start the next sprint?
