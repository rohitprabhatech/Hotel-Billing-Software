# Sprint 6 — Documentation + E2E Testing Guide

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Documentation only (no application or schema code changes)  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Bring manuals and the testing guide in line with the **current** SaaS architecture:

- Master Admin is not a tenant user
- Public register is **PENDING** until approve
- Plans, trials, activate/deactivate/suspend, platform audit
- Inspect-then-upgrade for the existing cloud database (never `02_schema.sql` on live data)

This sprint does **not**:

- inspect or migrate the live hosted database
- change APIs, UI, or schema
- add Alembic revisions for Phase 8

---

## New documents

| File | Purpose |
|------|---------|
| `docs/master-admin-manual.md` | Operator console: footer-dot login, approval, lifecycle, audit |
| `docs/security-architecture.md` | JWT kinds, guards, subscription as access control |
| `docs/tenant-isolation.md` | How `tenant_id` is scoped; isolation matrix |
| `docs/subscription-management.md` | Statuses, snapshots, Master operations |
| `docs/trial-management.md` | Defaults apply to new approvals only |
| `docs/plan-management.md` | Catalog + landing `GET /public/plans` |
| `docs/registration-approval-flow.md` | Pending → approve/reject |
| `docs/backup-and-recovery.md` | Backup, inspect, `apply_pending_schema.py`, rollback |
| `docs/privacy-policy.md` | Mirrors `/privacy` |
| `docs/terms-of-service.md` | Mirrors `/terms` (includes pending registration) |

---

## Updated existing docs

- `user-manual.md` / `owner-manual.md` / `billing-user-manual.md` — pending approval, trial/expiry lockout, no Pay button
- `test-business-billing-guide.md` — last updated 2026-08-18; Master, landing footer dot, Shree Family Restaurant registration, Professional ₹999 plan, 15 vs 30 day trial, activate/deactivate/suspend, expiry job, isolation, migration checklist; Script G now requires Master approve
- `deployment-guide.md` / root `README.md` / `docs/README.md` / `development-roadmap.md`

Outdated instruction removed: register no longer creates a tenant immediately or expects email-verify-then-login for public SaaS signup.

---

## Tests

No application code changed in this sprint.

Last backend regression (Sprint 5): **213 passed**.  
Re-run `pytest` when you want a fresh gate; it is not required to validate markdown-only edits.

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Master Admin manual exists and matches `/master/login` + footer dot | Yes |
| Security / tenant isolation / subscription / trial / plan / registration docs exist | Yes |
| Backup + inspect-before-migrate runbook exists | Yes |
| Privacy / Terms docs exist and point at live pages | Yes |
| E2E guide covers Master, landing, registration, isolation, plans, trial, expiry | Yes |
| Old “register → immediate owner login” wording removed from current manuals/guide | Yes |
| Live DB not migrated | Yes |

---

## Remaining (later sprints)

- Live inspect + non-destructive apply when `DATABASE_URL` is available
- Optional: Alembic coverage for Phase 8 tables
- Optional: Master `list_businesses` query performance
- Sprint 7-style final verification / signoff after cloud schema is confirmed

---

## Stop

Sprint 6 is complete.

Should I start the next sprint?
