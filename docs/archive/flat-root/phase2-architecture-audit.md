# Phase 2 Architecture Audit Report

**Sprint:** Phase 2 — P2-1  
**Date:** 2026-08-14  
**Product:** Business Billing (multi-tenant SaaS)  
**Stack:** Flask + SQLAlchemy + MySQL · React + MUI + Vite  
**Method:** Read-only inspection of current codebase (no feature code changes in this sprint)

**Related:** Phase 1 complete ([`final-qa-report.md`](./final-qa-report.md)) · Phase 2 plan ([`development-roadmap.md`](./development-roadmap.md)) · Relationships ([`database-relationships.md`](./database-relationships.md))

---

## 1. Executive summary

The application is a **working multi-business billing SaaS** after Phase 1 (Sprints 1–22). Phase 2 should **not rebuild**; it should improve commercial landing, category UX clarity, UI/responsive polish, measured performance, and grocery-focused testing.

| Dimension | Health | Phase 2 focus |
|-----------|--------|----------------|
| Backend domain / APIs | Strong | Verify + small consistency fixes |
| Tenant isolation | Strong (app-level) | Retest in P2-13 |
| Category hierarchy (BE) | Strong | Keep; FE copy polish in P2-4 |
| Landing / marketing UI | Adequate, not commercial | **P2-2 redesign** |
| Company contact data | **Outdated** | **P2-2** (`company.js`) |
| App UI consistency | Good shell; uneven pages | P2-6 / P2-7 |
| Performance | Acceptable for small tenants | P2-8 (N+1, pagination, code-split) |
| Docs / E2E sample data | Present; hotel-leaning seed | P2-12 grocery pack |

---

## 2. Frontend inventory

### 2.1 Routes (`frontend/src/routes`)

| Area | Paths | Guard |
|------|-------|-------|
| Public | `/` | None |
| Auth | `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email` | AuthLayout |
| Owner | `/owner/dashboard`, bills, items, item-activity, categories, reports, ai, audit, users, settings, profile, change-password | `OWNER` |
| Billing | `/billing`, `/billing/new`, bills, items, categories, profile, change-password | `OWNER` \| `BILLING_USER` |
| Print | `/print/bills/:billId` | Auth |

**Finding:** No `React.lazy` route splitting — entire page tree eager-loaded (`AppRoutes.jsx`).

### 2.2 Landing (`HomePage.jsx` + `constants/company.js`)

**Present:** Sticky nav, hero, Features, Modules, Businesses, Billing, Reports, AI, Security, Pricing (₹550 info), Contact, Footer, dark-mode toggle.

**Gaps vs Phase 2 brief:**
- No mobile hamburger; section links hidden on `xs`
- Long “wiki-style” section stack vs conversion funnel
- Hero uses external Unsplash image
- Nav labels differ from brief (missing dedicated AI Insights / About anchors as named)
- **Contact facts outdated** (single source):

| Field | Current (`company.js`) | Required (Phase 2) |
|-------|------------------------|--------------------|
| Address | Pune Satara Road, Khed-Shivapur, 412205 | B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune – 411041 |
| Email | support@prabhatech.in | prabha.technology.01@gmail.com |
| Phone | +91 20 7123 4567 | 8767865572 |

### 2.3 Categories UX

| Surface | Behavior |
|---------|----------|
| Owner `CategoriesPage` | Add/Edit dialog: Name, Description, Parent **Autocomplete** (`No Parent / Main Category`), helper text, hierarchy indent in table |
| Billing `BillingCategoriesPage` | Read-only hierarchy; no Path column |
| Items category picker | Plain `Select` (less hierarchy-aware) |

**BE already blocks:** self-parent, circular, cross-tenant parent, inactive parent.

**Phase 2-4:** Clarify helper copy; optional Path on billing list; hierarchical labels on Items picker.

### 2.4 Design system

- Theme: `theme/index.js` light + dark via `ColorModeContext` (`bbs-color-mode`)
- Shells: `OwnerLayout` / `BillingLayout` / `AuthLayout` + `MainContent` / `shell.js`
- Primitives: `PageHeader`, `PageShell`, `FilterBar`, `TableCard`, `EmptyState`, `KpiCard`

**Finding:** System exists; page-level density/empty/loading states still vary (P2-6).

### 2.5 List UX / pagination (FE)

| Page | Behavior |
|------|----------|
| Items | `per_page: 100`, no UI pager |
| Bills history | `per_page: 100`, no UI pager |
| New Bill catalog | `per_page: 60` |
| Audit / item activity | `per_page: 100` |
| Categories | Full tenant list |

---

## 3. Backend inventory

### 3.1 API surface (`/api/v1`)

| Blueprint | Prefix | Notes |
|-----------|--------|-------|
| health | `/health`, `/health/ready` | Public |
| auth | `/auth` | register-business, login, verify, reset, logout (+ legacy register-hotel) |
| profile | `/profile` | Auth |
| users | `/users` | Owner |
| tenants | `/tenants` | business-types public; me GET/PUT |
| categories | `/categories` | Write mostly Owner |
| items | `/items` | Soft status; DELETE forbidden |
| bills | `/bills` | Create/list/get/cancel/print; today-summary |
| reports | `/reports` | Owner |
| audit-logs | `/audit-logs` | Owner; no mutate |
| ai | `/ai` | Owner; analysis/decisions |

### 3.2 Tenant isolation pattern

1. JWT → `auth_required` (active user/tenant, role, `token_version`)  
2. `RequestContext.tenant_id`  
3. Repositories: `*_and_tenant` / `list_by_tenant`  

**No MySQL RLS.** Isolation is application-enforced (confirmed Sprint 21).

### 3.3 Category service (validation matrix)

| Rule | Status |
|------|--------|
| Parent exists in same tenant | ✅ |
| Cannot be own parent | ✅ |
| Cannot set descendant as parent | ✅ |
| Parent must be active | ✅ |
| Soft deactivate with children blocked | ✅ |
| Max depth limit | ❌ Not enforced |
| Root name uniqueness at DB | ✅ `parent_key` generated + unique (P2-5) |

### 3.4 Known consistency holes (for later sprints)

- ~~`ItemService.update_item` may not reject inactive category reassignment~~ ✅ fixed P2-5
- ~~Item list serialize can N+1 on `category` / `creator`~~ ✅ fixed P2-8
- Subscription is **informational FE only** — **no `subscriptions` table**

### 3.5 “Item activity”

Not a separate table. Owner UI filters **audit_logs** for item entity actions (create/update/status). Historical rows remain after item soft-deactivate.

---

## 4. Database relationship checklist

**Canonical schema:** `backend/sql/02_schema.sql`  
**Ops path for existing DBs:** `backend/scripts/apply_pending_schema.py`  
**Alembic:** `backend/migrations/versions/20260814_*.py` (+ earlier 20260326_*)

### 4.1 Entity map

```
roles (global)
   ▲
users ──tenant_id──► tenants
   │                   │
   ├─ password_reset_tokens
   ├─ email_verification_tokens
   │
tenants
   ├── categories (parent_id → categories.id, NULL = main)
   │      └── items (category_id, created_by → users SET NULL)
   ├── bill_number_counters
   ├── bills (created_by / cancelled_by → users)
   │      └── bill_items (item_id SET NULL; name/price/GST snapshots)
   └── audit_logs (user_id nullable)
```

**Not in schema:** `subscriptions` table (plan is FE constant ₹550/mo).

### 4.2 FK / cascade checklist

| Relationship | ON DELETE (schema intent) | App behavior | Checklist |
|--------------|---------------------------|--------------|-----------|
| `users.tenant_id → tenants` | RESTRICT | Soft deactivate users | ☐ Live DB matches |
| `users.role_id → roles` | RESTRICT | Seeded OWNER / BILLING_USER | ☐ |
| `categories.tenant_id → tenants` | RESTRICT | Soft `is_active` | ☐ |
| `categories.parent_id → categories` | RESTRICT | Self-ref hierarchy | ☐ |
| `items.tenant_id → tenants` | RESTRICT | Soft `is_active` | ☐ |
| `items.category_id → categories` | RESTRICT | Must exist | ☐ |
| `items.created_by → users` | SET NULL | Keep catalog | ☐ |
| `bills.tenant_id → tenants` | RESTRICT | Cancel only | ☐ |
| `bills.created_by / cancelled_by → users` | RESTRICT | Attribution | ☐ |
| `bill_items.bill_id → bills` | RESTRICT | No hard-delete bill | ☐ |
| `bill_items.item_id → items` | SET NULL | Snapshots survive | ☐ Verify on live DB |
| `audit_logs.tenant_id → tenants` | RESTRICT | Append-only API | ☐ |
| Auth tokens → users | CASCADE | Ephemeral | ☐ |

### 4.3 Indexes / uniques (expected)

| Table | Must-have |
|-------|-----------|
| tenants | `business_type`, status |
| users | `(tenant_id, email)` unique; tenant indexes |
| categories | `(tenant_id, parent_id, name)` unique; `parent_id`; tenant+active |
| items | tenant+name unique; tenant+sku unique; tenant+category; tenant+active |
| bills | tenant+bill_number / sequence unique; tenant+created_at; payment_method |
| bill_items | tenant+bill; tenant+item |
| audit_logs | tenant+created_at / action / entity |

### 4.4 Env drift note

Local DBs created before Phase 1 schema updates may miss columns (e.g. `tenants.business_type`, item SKU fields). **Symptom:** register-business → `Unknown column 'business_type'`.

**Remediation:** `python scripts/apply_pending_schema.py` (with `DATABASE_URL`) or `flask db upgrade` / re-apply `02_schema.sql` on empty DB.

### 4.5 Models vs SQL

| Model file | Table |
|------------|-------|
| `tenant.py` | tenants (+ `business_type`) |
| `user.py` | users |
| `role.py` | roles |
| `category.py` | categories |
| `item.py` | items (+ sku, cost_price, stock_quantity) |
| `bill.py` | bills, bill_items, bill_number_counters |
| `audit_log.py` | audit_logs |
| `auth_token.py` | password_reset_tokens, email_verification_tokens |

---

## 5. Documentation inventory

| Doc | Phase 2 action |
|-----|----------------|
| `development-roadmap.md` | Phase 2 plan present |
| `user-manual.md` / owner / billing manuals | Refresh after P2-2 / P2-4 / P2-12 |
| `test-business-billing-guide.md` | Expand grocery Shree General Store pack (P2-12) |
| `database-design.md` / `database-relationships.md` | Update if P2-5 changes schema |
| `api-documentation.md` | Spot-check after any API deltas |
| `deployment-guide.md` | Keep `apply_pending_schema` called out |
| `company.js` (FE) | Treat as source of truth for public contacts (P2-2) |

---

## 6. Risk register (Phase 2)

| ID | Risk | Mitigation sprint |
|----|------|-------------------|
| R1 | Landing redesign regresses dark mode / CTAs | P2-2 + manual dark check |
| R2 | Live DB missing columns after pull | P2-1 checklist + deploy guide |
| R3 | Perf work breaks billing cart | P2-8 + P2-9 |
| R4 | Over-scoping “full UI redesign” | P2-6 = consistency pass, not rewrite |
| R5 | Tenant leakage regressions | P2-13 automated + manual matrix |

---

## 7. Sprint P2-1 acceptance

| Criterion | Status |
|-----------|--------|
| Formal Phase 2 audit written | ✅ This document |
| DB relationship checklist published | ✅ §4 |
| No feature code changes in this sprint | ✅ |
| Roadmap points to this deliverable | ✅ (updated with Sprint P2-1 outcome) |

---

## 8. Recommended next sprint

**P2-2 — Landing / Home redesign + company contact update**

Do not start until product owner approves.
