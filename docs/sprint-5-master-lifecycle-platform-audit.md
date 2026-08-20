# Sprint 5 — Master Business Lifecycle + Platform Audit

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Give Master Admin a way to activate, deactivate, and suspend a business **without deleting data**, and record Master actions in a platform audit log (separate from tenant `audit_logs`).

This sprint does **not**:

- inspect or migrate the live hosted database
- drop tables or reset production data
- add a payment gateway
- mix Master Admin into tenant `users`

---

## Business lifecycle (no data delete)

| Action | API | Effect |
|--------|-----|--------|
| **Activate** | `POST /api/v1/master/businesses/:id/activate` | `tenants.status = ACTIVE` — login allowed |
| **Deactivate** | `POST /api/v1/master/businesses/:id/deactivate` | `tenants.status = SUSPENDED` — login blocked; bills, items, and users kept |
| **Suspend** | `POST /api/v1/master/businesses/:id/suspend` | `subscriptions.status = SUSPENDED` — login allowed, billing locked (402) |
| **Resume** | `POST /api/v1/master/businesses/:id/unsuspend` | Restores a suspended subscription; billing allowed if the period is still valid |

Owner/Billing tokens receive **403** on these endpoints.

---

## Platform audit

New table: `platform_audit_logs` (not tenant-scoped).

- Actor is a Master Admin (`actor_id` optional FK to `master_admins`)
- Optional `tenant_id` for business-related actions
- Passwords, hashes, and tokens are stripped before write
- Tenant `audit_logs` are unchanged

Logged actions include:

- `BUSINESS_APPROVED` / `BUSINESS_REJECTED`
- `BUSINESS_ACTIVATED` / `BUSINESS_DEACTIVATED` / `BUSINESS_SUSPENDED` / `BUSINESS_UNSUSPENDED`
- `PLAN_CREATED` / `PLAN_UPDATED` / `PLAN_ACTIVATED` / `PLAN_DEACTIVATED`
- `TRIAL_SETTINGS_UPDATED`
- `SUBSCRIPTION_UPDATED` (assign / trial / renew / cancel)

API: `GET /api/v1/master/audit-logs` (`action`, `entity_type`, `tenant_id`, `page`)  
UI: `/master/audit`

Existing hosted databases: apply with **`python scripts/apply_pending_schema.py`** (includes `apply_platform_audit.py`). That helper **creates** the table if missing; it does not drop data. Do **not** re-run `02_schema.sql` on production.

---

## Tests

| Check | Result |
|-------|--------|
| Backend pytest | **213 passed** |
| Frontend production build | **green** (1667 modules) |
| Owner cannot deactivate or read platform audit | 403 |
| Deactivate blocks login; tenant/user rows remain | Pass |
| Suspend allows login + profile; bills return 402 | Pass |
| Resume restores billing | Pass |
| Approve / plan / trial-settings / deactivate appear in audit | Pass |
| Secrets stripped from audit snapshots | Pass |

---

## Changed files (high level)

**Backend**

- `app/models/platform_audit_log.py` — new
- `app/repositories/platform_audit_repository.py` — new
- `app/services/platform_audit_service.py` — new
- `app/services/master_business_service.py` — new
- Registration, plan, trial-settings, and subscription services now write platform audit rows
- `app/routes/master_routes.py` / `app/controllers/master_controller.py`
- `scripts/apply_platform_audit.py` — idempotent CREATE
- `scripts/apply_pending_schema.py` / `scripts/inspect_database_schema.py` / `sql/02_schema.sql`
- `tests/test_sprint5_master_lifecycle_audit.py` — new

**Frontend**

- `pages/master/MasterBusinessesPage.jsx` — Activate / Deactivate / Suspend / Resume
- `pages/master/MasterAuditPage.jsx` — new
- Master layout nav, routes, `masterService.js`

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Activate / deactivate / suspend without deleting data | Yes |
| Deactivated business cannot sign in | Yes |
| Suspended subscription can sign in but cannot bill | Yes |
| Master actions recorded in platform audit | Yes |
| Passwords/tokens not stored in audit | Yes |
| Tenant isolation: Owner cannot call Master APIs | Yes |
| Live DB not migrated in this sprint | Yes |

---

## Stop

Sprint 5 is complete.

Should I start the next sprint?
