# Security Architecture — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Canonical API notes:** [api-documentation.md](./api-documentation.md)  
**Historical controls:** [17-security.md](./17-security.md) · [security-tenant-audit.md](./security-tenant-audit.md)

This document describes **the system as implemented**, not a target design.

**Schema / ops status:** 23 application tables; hosted DB stamped `20260818_phase8_saas`. Master Admin login requires a seeded `master_admins` row (`scripts/seed_master_admin.py`).

---

## Identity model

Two account kinds share `POST /api/v1/auth/login` but are stored separately:

| Kind | Table | JWT |
|------|-------|-----|
| Business user (OWNER / BILLING_USER) | `users` | `role`, **`tenant_id`**, `tv` (token version) |
| Master Admin | `master_admins` | `role=MASTER_ADMIN`, **no `tenant_id`**, `tv` |

Passwords are hashed. API responses never include `password` or `password_hash`.

Logout and password change bump `token_version` so prior JWTs fail.

---

## Authorization

| Guard | Used for |
|-------|----------|
| `auth_required` | Business APIs |
| `master_required` | `/api/v1/master/*` |
| Role allow-lists | Owner-only reports, users, audit, tenant settings |

Owner/Billing JWTs receive **403** on Master APIs. Master JWTs cannot call tenant billing APIs (no tenant context).

Frontend route guards are UX only. The API is the real control.

---

## Tenant isolation

See [tenant-isolation.md](./tenant-isolation.md).

Rule: **`tenant_id` is never trusted from the client.** Repositories/services scope by JWT / request context.

---

## Master entry path

- Public UI: subtle footer dot → `/master/login`
- No navbar “Master Admin Login”
- Owner credentials on `/master/login` are rejected in the UI with a generic error
- Backend still authenticates by email; Master authorization is the JWT role

---

## Subscription as an access control

| State | Login | Billing / catalog writes |
|-------|-------|--------------------------|
| Trial / Active / Expiring | Yes | Yes |
| Expired / Cancelled / Suspended subscription | Yes | **402** `SUBSCRIPTION_INACTIVE` |
| Tenant `status=SUSPENDED` (deactivated) | **No** (generic login failure; existing JWT → 401) | — |
| Registration `PENDING` | **No** | — |

Profile remains available when billing is locked (expired/cancelled/suspended subscription).

---

## Audit

| Log | Scope | Examples |
|-----|-------|----------|
| `audit_logs` | One tenant | LOGIN, CREATE_BILL, CANCEL_BILL, item/user changes |
| `platform_audit_logs` | Platform | BUSINESS_APPROVED, PLAN_UPDATED, BUSINESS_DEACTIVATED |

Platform audit strips `password`, `password_hash`, `token`, `access_token`, and similar keys before write.

Audit rows are append-only from the application. There is no Master or Owner API to edit/delete them.

---

## Secrets and delivery

- WhatsApp access tokens stored encrypted; never returned after save
- JWT and Flask secrets from environment; never commit `.env`
- Login rate limiting is enabled
- Mail may be suppressed locally (`MAIL_SUPPRESS_SEND`)

---

## What this architecture does not include

- Payment-gateway card checkout
- MySQL row-level security (RLS) — isolation is in application queries
- Mixing Master Admin into `users.tenant_id`
