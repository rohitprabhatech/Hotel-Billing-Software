# Phase 8 Sprint P8-1 — Architecture audit

**Date:** 2026-08-18  
**Status:** **COMPLETED** (docs only — no product code)  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Method:** Read-only inspection of current codebase  
**Branch:** `rs/feature/master-dashboard-18-8-26`

**Related:** [`development-roadmap.md`](./development-roadmap.md) · [`database-relationships.md`](./database-relationships.md) · [`security-tenant-audit.md`](./security-tenant-audit.md)

---

## 1. Executive summary

Business Billing is already a **working multi-tenant billing SaaS** (Owner + Billing User). It is **not** yet a billed platform with Prabha Technology as operator:

| Needed for this program | Current state |
|-------------------------|---------------|
| Master Admin dashboard | **Absent** — no `/master`, no platform role |
| Registration approval | **Absent** — Register Business creates tenant `ACTIVE` immediately |
| Plans / subscriptions | **Absent** in DB — ₹550 is a frontend constant |
| Trial / expiry / cron | **Absent** |
| Payment gateway | **Absent** (documented non-goal until now; still deferred) |
| Tenant isolation | **Present** — JWT → DB user → `ctx.tenant_id`; never from URL |

**Decision:** Do **not** rebuild Owner/Billing. Add a **third** identity and UI shell for Master Admin. Keep billing product APIs tenant-scoped.

---

## 2. Authentication audit

### 2.1 Flow

| Step | Behavior |
|------|----------|
| Register | `POST /api/v1/auth/register-business` — tenant + owner created; **no JWT** |
| Verify email | Required when `EMAIL_VERIFICATION_REQUIRED` (default true) |
| Login | `POST /api/v1/auth/login` — JWT 8h; claims `tenant_id`, `role`, `tv` |
| Session revoke | `users.token_version` must match claim `tv` |
| Roles | `OWNER`, `BILLING_USER` only (`VALID_ROLES`, SQL CHECK on `roles.name`) |

Key files: `backend/app/services/auth_service.py`, `backend/app/middleware/auth.py`, `backend/app/models/role.py`, `frontend/src/context/AuthContext.jsx`, `frontend/src/utils/authRouting.js`.

### 2.2 How tenant is resolved

`auth_required`:

1. Verify JWT  
2. Require `tenant_id` + `role` in `VALID_ROLES`  
3. Load user by identity  
4. Reject if `user.tenant_id != claim_tenant_id`  
5. Reject if tenant not `is_active()` (`status == "ACTIVE"`)  
6. Set `g.request_context` from **database user**, not the request URL  

Services use `require_request_context().tenant_id`. Repositories use `get_by_id_and_tenant`. Schemas use `unknown = EXCLUDE` so a forged body `tenant_id` is ignored.

**Implication for Master Admin:** current `auth_required` **cannot** authenticate a platform operator (it requires `tenant_id` and a business role). Sprint 2 must add a separate identity path (`master_admins` + `master_required`), not a fake “Prabha tenant” Owner account.

### 2.3 Frontend session

- `localStorage`: `access_token`, `auth_user` (role inside user JSON)  
- Unknown roles are **wiped** (`isValidRole`)  
- `GET /auth/me` exists but is **not** called on load  

Until `VALID_ROLES` includes the master role, a master JWT would fail client login even if the API issued it.

---

## 3. Tenant architecture audit

- All business tables carry `tenant_id` FK `ON DELETE RESTRICT`.  
- Isolation is **application-level** (no MySQL RLS).  
- Owner cannot change `tenants.status` via API (`UpdateTenantSchema` has no status).  
- Suspended tenants cannot log in (generic invalid-credentials) and cannot use authenticated APIs (`Tenant is suspended`).  
- Cross-tenant GET by UUID returns **404**, not 403.

**Keep:** never take `tenant_id` from URL/query/body/localStorage for authorization.  
**Master exception:** platform APIs may load a tenant **by id** only after `master_required` succeeds.

---

## 4. Registration audit

| Item | Today |
|------|--------|
| UI | `RegisterBusinessPage.jsx` — `/register` |
| Fields | Business name, type, address/city/state/pincode (optional), mobile, FSSAI if food type, owner name/email/password |
| GST | Not shown in UI; empty string posted |
| Terms checkbox | **Missing** |
| Auto-login | **No** — verify-email or login |
| Tenant status | **`ACTIVE` on create** |
| Approval | **None** |

This is a **behavior change** in Sprint 3, not a small flag: new signups must not become commercially usable until Master approval.

---

## 5. Subscription / plans audit

- **No** `subscriptions` / `subscription_plans` tables.  
- **No** Razorpay/Stripe/Cashfree (or similar) in app code.  
- Landing + Owner Settings + Terms use `SUBSCRIPTION_PLAN` in `frontend/src/constants/company.js` (`priceInr: 550`).  
- Bill `payment_method` `cash` \| `online` is **customer POS tender**, not SaaS checkout.

---

## 6. Database audit (relevant)

### `tenants.status`

CHECK: `ACTIVE` \| `SUSPENDED` only. Helper: `Tenant.is_active()` → `status == "ACTIVE"`.

**Do not** overload this column with TRIAL / EXPIRED. Those belong on `subscriptions`. Sprint 3 should add **`PENDING`** to the CHECK for pre-approval tenants.

### `users`

- `tenant_id` **NOT NULL**  
- Global unique `email`  
- `is_active`, `email_verified`, `token_version`

### Notifications / email / audit / cron

| System | Scope today |
|--------|-------------|
| `notifications` | Tenant; stock + delivery failures |
| Email | Verify, reset, password changed, optional login notice, bill PDF |
| `audit_logs` | Always `tenant_id` — Owner-only API |
| Scheduler | **None** (no APScheduler/Celery) |

---

## 7. Landing page pricing audit

Hardcoded in `company.js`, rendered by `HeroSection`, `PricingFooter` → `SubscriptionPlanInfo`. No `GET /public/plans`. Sprint 8 must make landing **API-driven** so Master-created ACTIVE public plans appear without a frontend edit.

---

## 8. Dashboards audit

| Dashboard | Route | Data |
|-----------|-------|------|
| Owner | `/owner/dashboard` | **This tenant** sales/stock/bills |
| Billing | `/billing` | **This tenant** today + new bill |
| Master | — | **Does not exist** |

OwnerLayout and BillingLayout are separate shells + `ProtectedRoute` role arrays. Master must follow that pattern (`MasterLayout` + `roles={['MASTER_ADMIN']}`), **not** extra nav on Owner.

Catch-all `*` → `/`. Visiting `/master` today shows the landing (or redirects logged-in owners to `/owner/dashboard`).

---

## 9. Reuse vs modify

### Reuse

JWT + `token_version`; `roles_required` pattern; request context; tenant-scoped repositories; `EmailService`; in-app notifications (new types later); `AuditService` idea (new **platform** table); `apply_pending_schema.py`; MUI shell primitives; dark mode.

### Modify (later sprints)

`auth_required` (or add `master_required` beside it); `VALID_ROLES` / `roles.name` CHECK; register path; `tenants.status` CHECK; landing pricing source; `authRouting.js` / `AppRoutes.jsx`.

### Do not reuse as Master UI

`OwnerDashboardPage`, Owner nav (items/bills/stock), `/tenants/me`, `NotificationBell` click maps (owner/billing paths).

---

## 10. Recommended additive schema (not applied in P8-1)

| Table | Purpose |
|-------|---------|
| `master_admins` | Platform operators; **no** `tenant_id` |
| `registration_requests` | PENDING / APPROVED / REJECTED + timestamps + reject reason |
| `subscription_plans` | Name, description, price, cycle, features JSON, `is_public`, `display_order`, `is_active` |
| `subscriptions` | Tenant entitlement; `plan_id`; `price_at_purchase`; trial/period dates; status |
| `platform_settings` | `trial_enabled`, `trial_days`, expiry warning days |
| `platform_audit_logs` | Master actions (separate from tenant `audit_logs`) |

**Price-change policy:** changing a plan’s price must **not** rewrite `subscriptions.price_at_purchase`. New price applies to new/renewals.

**Trial-toggle policy:** global ON/OFF affects **new eligible** approvals only, not existing trials/subscriptions.

**Payment:** leave `payment_status` / provider fields nullable so a gateway can be added without rebuilding subscriptions. Do **not** activate paid periods from a frontend flag.

---

## 11. API / frontend delta (planned, not built)

**API:** `master_required` on `/api/v1/master/*`; public `GET /api/v1/public/plans`; later tenant **subscription gate** on business APIs (expired → structured error). Owner/Billing routes stay; Master hitting them → 403; Owner hitting master → 403.

**Frontend:** `/master/*` + `MasterLayout`; register Terms + pending copy; landing fetch public plans.

---

## 12. Risks and migration concerns

1. **Lockout:** existing ACTIVE tenants have **no** subscription. Sprint 6 must grandfather (complimentary / assigned plan) **before** enforcing expiry.  
2. **Auth split:** Master cannot share `users.tenant_id NOT NULL`.  
3. **CHECK ALTERs** on `roles.name` and `tenants.status` (same care as prior delivery CHECK updates).  
4. **Global email uniqueness** vs pending registration emails.  
5. **No scheduler today** — expiry cannot depend on a user opening the app (Sprint 7).  
6. **Do not reset MySQL** or hard-delete financial rows.  
7. **Do not trust** frontend `role` or `localStorage` for Master access.

---

## 13. Phase 8 sprint map (implementation after P8-1)

| Sprint | Title | Code? |
|--------|-------|-------|
| **P8-1** | Architecture audit (this document) | Docs only |
| **P8-2** | Master Admin authentication + dashboard shell | Yes |
| **P8-3** | Business registration approval | Yes |
| **P8-4** | Trial management | Yes |
| **P8-5** | Plan management | Yes |
| **P8-6** | Subscription lifecycle + access gate | Yes |
| **P8-7** | Notifications, email, scheduled expiry job | Yes |
| **P8-8** | Dynamic landing pricing | Yes |
| **P8-9** | Security + tenant isolation | Tests + fixes |
| **P8-10** | Testing + documentation gate | Docs + tests |

**Explicit non-goals this phase:** payment-gateway checkout; rebuilding Owner/Billing; deleting billing history.

---

## P8-1 acceptance

| Criterion | Met? |
|-----------|------|
| Auth / tenant / registration / DB / landing / dashboards audited | Yes |
| Reuse vs modify listed | Yes |
| Proposed tables + policies documented | Yes |
| Risks (especially grandfather lockout) documented | Yes |
| No product schema or API changes in this sprint | Yes |

---

**Stopped.** Next: P8-2 Master Admin authentication + dashboard foundation — only after approval.
