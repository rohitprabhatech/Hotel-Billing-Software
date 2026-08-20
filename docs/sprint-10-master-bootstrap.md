# Sprint 10 — Live platform readiness + Master Admin bootstrap

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Confirm the hosted database is ready for Master login, and make first-admin seed safe and testable.

This sprint does **not**:

- invent or write a Master Admin password on the live database
- run `02_schema.sql`
- add Alembic revisions

Live seed is blocked until `MASTER_ADMIN_EMAIL` and `MASTER_ADMIN_PASSWORD` are set in the environment (they are still absent from `backend/.env`).

---

## Live readiness (read-only)

Command: `python scripts/check_platform_ready.py`

Saved: [`sprint-10-platform-ready.json`](./sprint-10-platform-ready.json)

| Check | Result |
|-------|--------|
| Target | `srv1952.hstgr.io` / `u583892242_HotelBillingDB` |
| Phase 8 tables missing | **none** |
| tenants / users / bills | 1 / 1 / 2 (unchanged) |
| subscription_plans / subscriptions | 1 / 1 |
| master_admins | **0** |
| Script exit code | **1** (schema OK, seed required) |

---

## Seed hardening

| Piece | Change |
|-------|--------|
| `MasterBootstrapService.seed_first` | Validates email/password; refuses a business-user email; idempotent |
| `scripts/seed_master_admin.py` | Loads `MYSQL_*` via Flask config; prints redacted host/database; requires `master_admins` table; does not overwrite |
| `scripts/check_platform_ready.py` | New read-only ops check |

---

## Tests

| Check | Result |
|-------|--------|
| `tests/test_sprint10_master_bootstrap.py` | Pass (4) |
| Full backend pytest | **228 passed** |
| Live Master Admin row created | **No** |

---

## Remaining (later sprints)

- Set `MASTER_ADMIN_*` and run `seed_master_admin.py` on the hosted DB
- Optional Alembic coverage for Phase 8 tables
- Final verification / signoff after the first Master can sign in at `/master/login`

---

## Stop

Sprint 10 is complete.

Should I start the next sprint?
