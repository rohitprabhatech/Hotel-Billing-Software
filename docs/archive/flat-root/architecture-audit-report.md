# Architecture Audit Report

**Project:** Hotel Billing Software → Multi-Business Billing SaaS  
**Sprint:** 1 — Codebase audit + architecture  
**Audit date:** 2026-08-14  
**Baseline commit:** `60aa84e` on branch `rohit-dev1`  
**Scope:** Read-only analysis. No feature or schema changes in this sprint.  
**Related:** [development-roadmap.md](./development-roadmap.md)

---

## 1. Executive summary

The codebase is a **working multi-tenant billing product** with solid layered architecture, JWT role auth, tenant-scoped data access, GST billing with historical line snapshots, parent categories, cash/online payment, reports, and audit trails.

It remains **hotel-domain branded** (copy, FSSAI, table numbers, registration API naming). Conversion to a **generic multi-business billing SaaS** is primarily:

1. Domain generalization (terminology + `business_type`)
2. Catalog enrichment (SKU / cost / optional stock)
3. New SaaS surfaces (landing, subscription info, AI, dark mode)
4. Schema/process hardening (single migration story, email policy, security pass)

**Do not rebuild.** Extend and rename on the existing foundation.

---

## 2. Current architecture

### 2.1 Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, SQLAlchemy, Marshmallow, Flask-JWT-Extended, MySQL |
| Frontend | React 19, Vite 8, MUI 9, React Router 7, Axios, Recharts |
| Auth | JWT with claims `tenant_id`, `role`, `tv` (token version) |
| Tenancy | Shared database + application-enforced `tenant_id` |

### 2.2 Backend layering

```
HTTP Request
  → routes/*.py          (blueprints under /api/v1)
  → middleware/auth.py   (JWT + roles_required)
  → controllers/*.py     (parse request, call service)
  → schemas/*.py         (Marshmallow validation)
  → services/*.py        (business rules + audit writes)
  → repositories/*.py    (tenant-scoped queries)
  → models/*.py          (SQLAlchemy ORM)
  → MySQL
```

**App factory:** `backend/app/__init__.py`  
**Config:** `backend/app/config/settings.py`  
**API registration:** `backend/app/routes/__init__.py`

### 2.3 API surface (`/api/v1`)

| Blueprint | Responsibility |
|-----------|----------------|
| `health` | Health / readiness |
| `auth` | Login, register-hotel, verify, forgot/reset password, logout, me |
| `profile` | Profile + change password |
| `users` | Owner manages billing users |
| `tenants` | Current tenant read/update |
| `categories` | Category CRUD + hierarchy |
| `items` | Item CRUD + activate/deactivate |
| `bills` | Create, list, cancel, print meta, today-summary |
| `reports` | Owner sales analytics + export |
| `audit-logs` | Owner audit list/detail/alerts |

### 2.4 Frontend structure

```
frontend/src/
  routes/          AppRoutes, ProtectedRoute, paths
  layouts/         AuthLayout, OwnerLayout, BillingLayout
  pages/           auth, account, owner, billing, bills, reports, print
  components/      PageShell, FilterBar, KpiCard, TableCard, …
  context/         AuthContext, PageActionsContext
  services/        apiClient + domain services
  theme/           light-only MUI theme
  print/           PrintableReceipt
```

**Public routes:** `/`, `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email`  
**Owner:** `/owner/*`  
**Billing (OWNER or BILLING_USER):** `/billing/*`, `/print/bills/:billId`

### 2.5 Data model (logical)

```
Tenant
 ├── Users ──► Role (OWNER | BILLING_USER)   [roles are global]
 ├── Categories (parent_id → categories)
 │     └── Items (created_by → users)
 ├── BillNumberCounter
 ├── Bills
 │     └── BillItems (name/price/GST snapshots; item_id nullable)
 ├── AuditLogs
 └── Auth tokens (password_reset, email_verification) via User
```

**Physical schema source of truth (canonical SQL):** `backend/sql/02_schema.sql`  
**Incremental alters:** `backend/sql/03_saas_auth_alter.sql`  
**Alembic revisions:**

- `20260326_saas_auth_tokens.py`
- `20260326_item_created_by.py`
- `20260326_bill_payment_method.py`

---

## 3. Feature readiness matrix

| Capability | Status | Notes for multi-business conversion |
|------------|--------|-------------------------------------|
| Multi-tenant isolation | ✅ Strong | Manual filters; covered by tests |
| JWT + roles | ✅ | OWNER / BILLING_USER only |
| Self-serve registration | ✅ Hotel-named | Rename to Register Business |
| Email verify / reset / change password | ✅ | Keep; update email copy |
| Parent categories | ✅ | Circular/self/cross-tenant checks exist |
| Items + soft deactivate + created_by | ✅ | No SKU/stock/cost yet |
| Billing + GST + discount | ✅ | Backend-authoritative |
| Remove line from cart (pre-generate) | ✅ UI | Does not delete catalog item |
| Payment method cash/online | ✅ | End-to-end present |
| Bill history + print + cancel | ✅ | Soft cancel; snapshots preserved |
| Owner dashboard | ✅ | Hotel copy; add business_type later |
| Reports + export | ✅ | OWNER only |
| Audit + item activity | ✅ | Append-only from app |
| Landing / marketing page | ❌ Minimal | Health card only |
| business_type | ❌ Missing | Required for Sprint 2 |
| Subscription UI | ❌ | Informational ₹550 later |
| AI assistant / prediction | ❌ | Sprints 13–14 |
| Dark mode | ❌ | Light theme only |
| Platform admin / multi-branch | ❌ Out of current scope | |

---

## 4. Hotel-specific assumptions inventory

| Assumption | Evidence | Conversion action (later sprints) |
|------------|----------|-----------------------------------|
| Product name “Hotel Billing” | API root, `HomePage`, layouts, `index.html` | Rebrand to Business Billing |
| Register Hotel | `RegisterHotelPage`, `/auth/register-hotel`, `hotel_name` | Register Business + fields |
| FSSAI required in UX | Tenant settings, receipt | Optional / type-contextual |
| `table_number` | `bills.table_number` | Optional reference/counter note |
| No business type | `tenants` table | Add `business_type` |
| Seed “Hotel A/B” | `seed_demo_data.py` | Multi-business demo tenants |
| Role seed text “Hotel owner…” | `02_schema.sql` | Business owner wording |
| Docs hotel-centric | `docs/01-*`, `22-*`, test guide | Refresh in Sprint 19 |

---

## 5. Tenant isolation assessment

### Strengths

- JWT identity loads user from DB; `tenant_id` taken from user, not client body
- Repositories commonly use `*_and_tenant` / `filter(tenant_id=…)`
- Isolation covered in: `test_tenant_isolation.py`, `test_billing.py`, `test_categories_items.py`, `test_reports.py`, `test_audit_logs.py`, `test_saas_registration_auth.py`

### Risks

| Risk | Severity | Detail |
|------|----------|--------|
| Manual scoping | High (process) | New queries can omit `tenant_id`; no RLS |
| Email policy mismatch | Medium | DB: unique `(tenant_id, email)`; register/login: global email lookup → ambiguity if duplicates exist |
| Logout | Low–Medium | No JWT blacklist; relies on expiry + `token_version` |
| Within-tenant power | Product | BILLING_USER can manage items and cancel any tenant bill |

**Verdict:** Cross-tenant IDOR for core entities appears well controlled today. Conversion sprints must preserve repository discipline and expand isolation tests for new fields/endpoints.

---

## 6. Database relationship notes

### Sound patterns

- Tenant RESTRICT on business tables (no accidental cascade wipe)
- Category self-FK with RESTRICT
- Bill items snapshot columns for historical accuracy
- Soft deactivate for items/categories (app forbids hard delete of financial data)
- Unique bill numbers/sequences per tenant
- `payment_method` constrained to `cash` \| `online`

### Issues / inconsistencies

| Issue | Detail |
|-------|--------|
| Bill status default | SQL default `DRAFT`; app creates `FINALIZED`; `VOID` unused |
| Dual apply paths | Full SQL + Alembic + Python apply scripts → drift risk |
| No `business_type` | Blocks multi-business classification |
| `fssai_number` | Hotel/F&B-specific; should be optional for retail |
| Items unique name | Inactive item still blocks same name (`uq_items_tenant_name`) |
| No subscription table | Acceptable until Sprint 16 (info-only may not need DB) |

---

## 7. Duplicate / split code observations

| Observation | Paths | Recommendation |
|-------------|-------|----------------|
| Audit write vs read repos | `audit_repository.py` vs `audit_log_repository.py` | Document; optional merge later |
| Schema apply scripts | `sql/apply_schema.py` + `scripts/apply_*.py` | Consolidate in Sprint 4 |
| Bills history shared page | Owner + billing wrappers → `BillsHistoryPage` | Keep (good reuse) |
| Hotel string literals | Scattered FE/BE | Systematic rename Sprint 2–3 / 17 |

---

## 8. Documentation inventory

| Document | Usefulness for SaaS conversion |
|----------|--------------------------------|
| `01`–`19` architecture/requirements | Core design still valid; hotel wording outdated |
| `20-development-sprints.md` | Historical hotel MVP sprints (complete) — superseded by `development-roadmap.md` |
| `21-production-readiness.md` | Still useful ops checklist |
| `22-saas-hotel-registration.md` | Accurate for current hotel register APIs |
| `test-hotel-billing-guide.md` | Manual QA baseline; rename later |
| `development-roadmap.md` | **Active** multi-business sprint plan |
| This report | Sprint 1 deliverable |

**Gap:** No `docs/README.md` index existed before Sprint 1 (added as part of this sprint).

---

## 9. Testing inventory & gaps

### Existing automated suites (`backend/tests/`)

| File | Focus |
|------|--------|
| `test_health.py` | Health endpoint |
| `test_auth.py` | Login / me / RBAC baseline |
| `test_saas_registration_auth.py` | Register, verify, reset, change password |
| `test_tenant_isolation.py` | Cross-tenant denial |
| `test_categories_items.py` | Catalog + hierarchy + isolation |
| `test_billing.py` | Totals, payment, snapshots, bill numbers |
| `test_billing_item_management.py` | Billing-user item CRUD + audit |
| `test_print_cancel.py` | Print/cancel/search |
| `test_reports.py` | Metrics/export/isolation |
| `test_audit_logs.py` | Filters/alerts/isolation |
| `test_money.py` | GST/discount math |
| `test_production_readiness.py` | Hardening checks |

### Gaps for multi-business SaaS

- `business_type` / Register Business flows
- SKU / stock / cost price
- Email collision across tenants + login disambiguation
- DRAFT/VOID workflows (if ever enabled)
- Dark mode, AI, subscription
- Frontend automated tests (minimal/none observed)
- Load test for concurrent bill numbering

---

## 10. Known bugs / product risks (non-exhaustive)

1. Hotel-only UX blocks non-hotel adoption messaging.  
2. Email uniqueness semantics inconsistent between DB and auth service.  
3. Schema default `DRAFT` vs app `FINALIZED` confusion for operators.  
4. Profile “phone” effectively updates tenant phone (not a separate user phone model).  
5. Receipt fallback brand can show “HOTEL”.  
6. Default DB name / sender still hotel-oriented (`hotel_billing`, hotelbilling.local).  
7. Manual tenant filtering remains a footgun for future developers.

---

## 11. Recommended conversion sequence (confirmed)

Matches `development-roadmap.md`:

1. **Sprint 1** — This audit (complete when accepted)  
2. **Sprint 2** — Tenant foundation + `business_type`  
3. **Sprint 3** — Register Business / auth rename  
4. **Sprint 4** — Schema/migration alignment  
5. **Sprints 5–12** — Harden existing catalog/billing/reports/audit with generic terminology  
6. **Sprints 13–18** — AI, landing, subscription info, UI pass, dark mode  
7. **Sprints 19–22** — Docs, E2E, security, final QA  

---

## 12. Sprint 1 completeness checklist

- [x] Backend architecture inspected  
- [x] Frontend architecture inspected  
- [x] Database models / SQL / migrations inventoried  
- [x] Auth / tenant isolation assessed  
- [x] Hotel-specific assumptions listed  
- [x] Duplicate/schema risks listed  
- [x] Documentation inventory captured  
- [x] Testing gaps identified  
- [x] Audit report published (`docs/architecture-audit-report.md`)  
- [x] Roadmap cross-linked  
- [x] Docs index created (`docs/README.md`)  
- [x] No feature/schema code changes in Sprint 1  

---

## 13. Out of scope (explicitly not done in Sprint 1)

- Renaming APIs or UI copy  
- Adding `business_type` or other schema fields  
- Landing page / dark mode / AI / subscription  
- Refactoring repositories or migrations  

---

**Sprint 1 status:** COMPLETED (pending product-owner acknowledgment)  

**Next:** Sprint 2 — Multi-business / tenant foundation  

Ask before starting: *Should I start Sprint 2?*
