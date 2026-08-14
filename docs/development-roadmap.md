# Development Roadmap — Multi-Business Billing SaaS

**Provider:** Prabha Technology Pvt. Ltd.  
**Project:** Hotel Billing Software → Generic Multi-Business Billing SaaS  
**Branch baseline:** `rohit-dev1` @ `60aa84e`  
**Roadmap date:** 2026-08-14  
**Rule:** One sprint at a time. Implement → Test → Report → **STOP** → Wait for approval.

---

## 0. Project audit summary (Phase 0)

### What already exists (do not rebuild)

| Area | Status | Notes |
|------|--------|-------|
| Multi-tenant Flask + React/MUI app | ✅ | Layered MVC: routes → controllers → services → repositories → models |
| JWT auth + OWNER / BILLING_USER | ✅ | `token_version` invalidation on password change |
| Self-serve registration | ✅ | Hotel-named (`/register`, `register-hotel` API) |
| Email verify / forgot / reset / change password | ✅ | Email templates present |
| Categories + parent hierarchy | ✅ | Circular/self-parent/cross-tenant checks exist |
| Items CRUD + soft deactivate + `created_by` | ✅ | Billing users can manage items; owner item activity |
| Billing (discount, GST CGST/SGST, finalize) | ✅ | Line items snapshot historical price/name/GST |
| Payment method Cash / Online | ✅ | Stored on bill; shown in history/print/reports/dashboard |
| Bill history + print + cancel | ✅ | Soft cancel with reason; no hard delete |
| Owner dashboard + reports + export | ✅ | Cash/online KPIs; xlsx/csv/pdf |
| Audit logs + item activity | ✅ | Append-only; owner alerts |
| Shared UI system | ✅ | PageShell, FilterBar, KpiCard, TableCard, etc. |
| Isolation tests | ✅ | Multiple pytest modules cover cross-tenant denial |

### Current architecture (high level)

```
React (Vite) SPA ──JWT──► Flask /api/v1 ──► MySQL (shared DB, tenant_id isolation)
     │                         │
  Owner / Billing layouts   Controllers → Services → Repositories → Models
```

**Core model tree today:**

```
Tenant
 ├── Users (OWNER, BILLING_USER)
 ├── Categories (parent_id self-FK)
 │     └── Items (created_by)
 ├── Bills
 │     └── BillItems (price/name/GST snapshots)
 ├── BillNumberCounter
 └── AuditLogs
```

**Roles:** Global `roles` table — only `OWNER` and `BILLING_USER`.

**Isolation:** Manual — JWT → request context `tenant_id` → every repository filters by tenant. No DB RLS.

### Hotel-specific assumptions (must generalize)

| Finding | Location (examples) |
|---------|---------------------|
| Product name “Hotel Billing” | `app/__init__.py`, `HomePage`, layouts, `index.html` |
| Register Hotel / `hotel_name` / `register-hotel` | Auth UI + `auth_service` / routes |
| `fssai_number` (food license) | Tenant model, settings, receipt |
| `table_number` on bills | Bill model / new bill / history |
| No `business_type` | Tenant model |
| Seed data “Hotel A / Hotel B” | `seed_demo_data.py` |
| Docs still hotel-centric | `docs/01-*`, `22-saas-hotel-registration.md`, test guide |

### Problems / risks found

1. **Domain naming** — UI/API/docs say “hotel”; blocks multi-business positioning.
2. **Missing `business_type`** — cannot classify restaurant vs retail vs grocery.
3. **No SKU / stock / cost price** — catalog is price+GST only.
4. **Email uniqueness ambiguity** — DB unique `(tenant_id, email)` but register/login use global email lookup.
5. **Dual schema paths** — `sql/02_schema.sql` + Alembic + ad-hoc apply scripts (drift risk).
6. **DRAFT/VOID statuses unused** — SQL allows them; app always creates `FINALIZED`.
7. **No subscription / plan model** — only marketing placeholder needed later.
8. **No AI assistant** — not started.
9. **Light theme only** — no dark mode / persistence.
10. **Landing page** — minimal health card, not SaaS marketing page.
11. **Manual tenant filters** — new queries can forget `tenant_id` (process risk).
12. **Docs drift** — `docs/20-development-sprints.md` marks hotel MVP complete; FE architecture docs miss newer routes.

### Testing gaps (high level)

- No business-type / non-hotel registration tests
- No SKU/stock tests
- Limited suspended-tenant edge cases
- No AI / dark-mode / subscription tests
- Login ambiguity if same email ever exists in two tenants

---

## 1. Sprint strategy (adjusted to codebase)

The user’s master list is preserved, but **order and scope are adjusted** because many mid-sprints already ship. Later sprints are **harden / generalize / verify**, not greenfield rebuilds.

| Sprint | Title | Nature |
|--------|-------|--------|
| 1 | Codebase audit + architecture report | Docs only |
| 2 | Multi-business / tenant foundation | Schema + rename foundation |
| 3 | Business registration + authentication | Rename/generalize existing flow |
| 4 | Database relationship refactor | Migrations + constraints audit |
| 5 | Category + parent category | Verify + UX polish |
| 6 | Items module (generic catalog) | SKU/cost/stock options + copy |
| 7 | Billing module | Verify cart remove + terminology |
| 8 | Payment method | Verify + close gaps |
| 9 | Bill history + printing | Historical snapshot + generic labels |
| 10 | Owner / business dashboard | Business name/type KPIs |
| 11 | Reports + analytics | Harden + terminology |
| 12 | Audit + user activity | Harden + terminology |
| 13 | AI business assistant | New feature |
| 14 | AI prediction + decision support | New feature |
| 15 | Public home / landing page | New marketing UI |
| 16 | Subscription (info only) | Plan display ₹550/mo — no gateway |
| 17 | Professional UI/UX pass | Cross-app consistency |
| 18 | Dark mode | Theme + persist |
| 19 | Documentation refresh | Reflect actual product |
| 20 | Complete E2E testing guide | Manual + automated |
| 21 | Security + tenant audit | Hardening pass |
| 22 | Final QA + production readiness | Release gate |

**Execution rule:** After each sprint → report → ask for approval before the next.

---

## 2. Sprint details

### Sprint 1 — Codebase audit + architecture

**Goal:** Formalize Phase 0 findings into an architecture audit report. No major feature changes.

**Tasks:**
- Confirm architecture layers and data model
- Inventory hotel-specific assumptions
- Inventory duplicates, schema risks, isolation risks, test gaps
- Publish audit report under `docs/`

**Deliverable:** `docs/architecture-audit-report.md` (+ this roadmap)

**Out of scope:** Feature renames, schema migrations, UI redesign

---

### Sprint 2 — Multi-business / tenant foundation

**Goal:** Tenant = generic Business.

**Tasks:**
- Add `business_type` (selectable options; not hardcoded into billing logic)
- Review Tenant fields: Business Name, Owner, `tenant_id`
- Make FSSAI optional / business-type contextual (not required for clothing/grocery)
- Begin replacing hotel-centric API/product strings at foundation level
- Verify tenant isolation remains intact

**Acceptance:** New businesses can store a type; existing tenants keep working.

---

### Sprint 3 — Business registration + authentication

**Goal:** Public “Register Business” flow (not “Register Hotel”).

**Tasks:**
- Rename UI/API copy: Register Business
- Fields: Business Name, Business Type, Owner Name, Email, Mobile, Password, Confirm Password, Address
- Keep: Create tenant → create owner → verify email → login → owner dashboard
- Update auth emails and validation messages

**Acceptance:** End-to-end register/login with business terminology; hotel wording gone from auth surfaces.

---

### Sprint 4 — Database relationship refactor

**Goal:** Correctness and single source of truth for schema.

**Tasks:**
- Review PKs/FKs/indexes/`tenant_id`/cascades/nullables/uniques
- Align `02_schema.sql` + Alembic + apply scripts
- Document cascade behavior for categories/items/bills
- Migrations for Sprint 2–3 fields if not already applied

**Acceptance:** Schema docs match live models; migration path clear for fresh and upgrade installs.

---

### Sprint 5 — Category + parent category

**Goal:** Confirm hierarchy is production-ready for any business.

**Tasks:**
- Verify self-parent / circular / cross-tenant prevention (backend + UI)
- Parent dropdown = current tenant only
- UX polish on `/owner/categories`
- Samples for Food and Clothing hierarchies in docs/tests

**Acceptance:** Existing hierarchy rules remain; UI copy is business-generic.

---

### Sprint 6 — Items module

**Goal:** Generic catalog.

**Tasks:**
- Add/support fields as appropriate: SKU, description, category, price, cost price (if supported), GST/tax, stock (if supported), status
- Keep billing-user add/edit/deactivate rules
- Owner item activity remains visible after deactivate
- Generic labels (not “menu item”)

**Acceptance:** Items usable for retail and F&B; activity trail intact.

---

### Sprint 7 — Billing module

**Goal:** Counter billing usable for any business.

**Tasks:**
- Verify search, categories, qty, remove-from-cart (not DB delete), discount, GST, totals, generate, print
- Generalize `table_number` (e.g. optional reference / table / counter note)
- Keep backend-authoritative totals

**Acceptance:** Mistaken cart lines removable before generate; calculations unchanged and correct.

---

### Sprint 8 — Payment method

**Goal:** Close any gaps around Cash / Online.

**Tasks:**
- Verify radio default Cash; persistence; history; print; reports; dashboards
- Fill any missing labels/filters
- Regression tests

**Acceptance:** Cash/Online visible end-to-end for every new bill.

---

### Sprint 9 — Bill history + printing

**Goal:** Historical integrity + generic receipts.

**Tasks:**
- Confirm BillItem snapshots (old price preserved after catalog price change)
- Bill numbering, details, print, cancel
- Receipt header uses Business Name (not “HOTEL” fallback)

**Acceptance:** Price-change regression test still passes; print is business-branded.

---

### Sprint 10 — Owner / business dashboard

**Goal:** Professional business dashboard.

**Tasks:**
- Show Business Name, Business Type
- KPIs: today sales/bills/avg/cancelled, cash/online, weekly/monthly
- Clean KPI cards; remove hotel-only copy

**Acceptance:** Dashboard reads as multi-business SaaS, not hotel-only.

---

### Sprint 11 — Reports + analytics

**Goal:** Owner performance review.

**Tasks:**
- Daily/weekly/monthly + filters
- Total sales, bill count, avg, top/low items, category sales, cash/online
- Generic terminology in UI/exports

**Acceptance:** Reports remain OWNER-only and tenant-scoped.

---

### Sprint 12 — Audit + user activity

**Goal:** Immutable operational trail.

**Tasks:**
- Verify item create/edit/deactivate, bill create/cancel, login, password change
- Item activity survives deactivate
- Owner-only read; no delete for normal users
- Generic copy

**Acceptance:** Audit/item-activity cover required events; isolation holds.

---

### Sprint 13 — AI business assistant

**Goal:** Tenant-scoped analysis of real sales data.

**Tasks:**
- Today / weekly / monthly / custom range analysis
- Sales, bills, top/low items, categories, payment mix, trends
- Never invent numbers; insufficient-data message when needed

**Acceptance:** AI only sees current tenant data.

---

### Sprint 14 — AI prediction + decision support

**Goal:** Recommendations from history.

**Tasks:**
- Best/slow movers, trends, demand hints, recommendations
- Explicit insufficient-data handling
- Tenant isolation mandatory

**Acceptance:** No fabricated metrics.

---

### Sprint 15 — Public home / landing page

**Goal:** Professional SaaS landing at `/`.

**Sections:** Hero, Features, Modules, Supported Businesses, Billing, Reports, AI, Security, Subscription, Contact, 24/7 Support, Footer  

**Company block:** Prabha Technology Pvt. Ltd. (Pune address, email, phone)  

**Acceptance:** No hotel-only positioning; CTAs Register Business + Login.

---

### Sprint 16 — Subscription (informational)

**Goal:** Show plan ₹550 / month.

**Tasks:**
- Landing + settings/subscription info
- Register / Login / Contact CTAs
- **No payment gateway** unless later required

**Acceptance:** Pricing visible; no fake paid checkout.

---

### Sprint 17 — Professional UI/UX

**Goal:** Consistency across every page.

**Tasks:** Spacing, typography, tables, forms, dialogs, sidebar, responsive layout  
**Avoid:** overlap, horizontal overflow, crowded sections, huge controls, wasted whitespace  

**Acceptance:** Shared design system applied consistently.

---

### Sprint 18 — Dark mode

**Goal:** Light / Dark with persistence.

**Surfaces:** Home, auth, owner, billing, reports, items, categories, users, audit, settings, AI  

**Acceptance:** Preference survives refresh.

---

### Sprint 19 — Documentation

**Goal:** Docs match implementation.

**Create/update:**
- `docs/README.md`
- `docs/development-roadmap.md` (this file)
- `docs/database-design.md` (or refresh `07`)
- `docs/api-documentation.md` (or refresh `09`)
- `docs/user-manual.md`, `owner-manual.md`, `billing-user-manual.md`
- `docs/test-business-billing-guide.md`
- `docs/deployment-guide.md`

**Acceptance:** Terminology is Business, not Hotel.

---

### Sprint 20 — Complete testing

**Goal:** Full E2E guide + automated coverage where practical.

**Cover:** Registration, roles, isolation, categories/parents, items, billing cart remove, discount/GST, cash/online, print/history, reports, audit, AI, dark mode, password/settings/subscription  

**Acceptance:** Guide uses realistic multi-business sample data.

---

### Sprint 21 — Security + tenant audit

**Goal:** Prove Business A cannot access Business B.

**Tasks:** JWT, RBAC, isolation, IDOR, password handling, route guards, audit immutability  

**Acceptance:** Written security findings + fixes for critical issues.

---

### Sprint 22 — Final QA + production readiness

**Goal:** Release gate.

**Tasks:** Backend/frontend/API/DB/tenant/UI/responsive checks; no broken routes/console/API/migration/tenant leakage; final QA report  

**Acceptance:** Signed-off QA report.

---

## 3. Terminology standard (all future sprints)

| Prefer | Avoid |
|--------|--------|
| Business | Hotel (as product default) |
| Business Owner | Hotel Owner |
| Business User / Billing User | Hotel Staff (as only framing) |
| Business Dashboard | Hotel Dashboard |
| Register Business | Register Hotel |
| Business Items / Categories | Hotel Menu (as only framing) |

Hotel remains a **valid business type**, not the product identity.

---

## 4. Technology constraints

- Backend: Python, Flask, REST, SQLAlchemy, MySQL
- Frontend: React, MUI, Vite
- Keep existing layered architecture
- Do not introduce unnecessary frameworks
- Do not rebuild from scratch

---

## 5. Current status

| Item | Status |
|------|--------|
| Phase 0 audit | ✅ Completed (2026-08-14) |
| `docs/development-roadmap.md` | ✅ Created |
| Sprint 1 — Architecture audit report | ✅ Completed (2026-08-14) |
| Deliverable | [`architecture-audit-report.md`](./architecture-audit-report.md) |
| Docs index | [`README.md`](./README.md) |
| Sprint 2 — Multi-business / tenant foundation | ✅ Completed (2026-08-14) |
| Sprint 3 — Business registration + authentication | ✅ Completed (2026-08-14) |
| Sprint 4 — Database relationship refactor | ✅ Completed (2026-08-14) |
| Sprint 5 — Category + parent category | ✅ Completed (2026-08-14) |
| Sprint 6 — Items module | ✅ Completed (2026-08-14) |
| Sprint 7 — Billing module | ✅ Completed (2026-08-14) |
| Sprint 8 — Payment method | ✅ Completed (2026-08-14) |
| Sprint 9 — Bill history + printing | ✅ Completed (2026-08-14) |
| Sprint 10 — Owner / business dashboard | ✅ Completed (2026-08-14) |
| Sprint 11 — Reports + analytics | ✅ Completed (2026-08-14) |
| Sprint 12 — Audit + user activity | ✅ Completed (2026-08-14) |
| Sprint 13 — AI business assistant | ✅ Completed (2026-08-14) |
| Sprint 14 — AI prediction + decision support | ✅ Completed (2026-08-14) |
| Sprint 15 — Public home / landing page | ✅ Completed (2026-08-14) |
| Sprint 16 — Subscription (informational) | ✅ Completed (2026-08-14) |
| Sprint 17 — Professional UI/UX pass | ✅ Completed (2026-08-14) |
| Sprint 18 — Dark mode | ✅ Completed (2026-08-14) |
| Sprint 19 — Documentation refresh | ✅ Completed (2026-08-14) |
| Sprint 20 — Complete E2E testing | ✅ Completed (2026-08-14) |
| Sprint 21 — Security + tenant audit | ✅ Completed (2026-08-14) |
| Sprint 22 — Final QA + production readiness | ✅ Completed (2026-08-14) |

**Program status:** Multi-business SaaS conversion sprints **1–22 complete**. Next: staging pilot + production cutover per [final-qa-report.md](./final-qa-report.md).

---

## 6. Sprint 22 outcome

1. ✅ Full backend `pytest` green; frontend `npm run build` green  
2. ✅ Route / API / tenant / UI release checklist documented  
3. ✅ Final QA report: [`final-qa-report.md`](./final-qa-report.md)  
4. ✅ Production readiness checklist refreshed: [`21-production-readiness.md`](./21-production-readiness.md)  
5. ✅ No Critical open defects at release gate; residual items non-blocking  

**Next for product owner:** Approve staging deployment and run E2E Script A + C on staging.

---

## Appendix — Sprint 21 outcome (prior)

1. ✅ Security audit report: [`security-tenant-audit.md`](./security-tenant-audit.md) — Business A ↛ Business B confirmed  
2. ✅ Fixes: logout / deactivate revoke JWT; global email uniqueness; reset & verify token stacking closed; proxy IP gated  
3. ✅ New tests: `tests/test_security_hardening.py`  
4. ✅ No Critical IDOR open; residual items documented (DB email unique index, shorter JWT TTL optional)  

**Prior next question:** Should I start Sprint 22?

---

## Appendix — Sprint 20 outcome (prior)

1. ✅ Expanded [test-business-billing-guide.md](./test-business-billing-guide.md) with B1–B3 multi-business sample pack, auto/manual matrix, and E2E scripts  
2. ✅ New automated gaps: `tests/test_sprint20_gaps.py` (suspended tenant, bill qty/empty/merge/discount cap, register other/invalid/default type, tenant settings fields, SKU tenant-scope, billing blocked from weekly/export)  
3. ✅ Dark mode + subscription UI remain documented as manual-only  
4. ✅ Gap suite green (`pytest tests/test_sprint20_gaps.py`)  

**Prior next question:** Should I start Sprint 21?

---

## Appendix — Sprint 19 outcome (prior)

1. ✅ Docs index + root README use **Business Billing** terminology  
2. ✅ New canonical docs: `database-design.md`, `api-documentation.md`, `deployment-guide.md`  
3. ✅ Manuals: `user-manual.md`, `owner-manual.md`, `billing-user-manual.md`  
4. ✅ `test-business-billing-guide.md` (supersedes hotel test guide for naming)  
5. ✅ Hotel-era docs marked historical / superseded where needed  

**Prior next question:** Should I start Sprint 20?

---

## Appendix — Sprint 18 outcome (prior)

1. ✅ Light / Dark themes via `createAppTheme(mode)` + `ColorModeProvider`  
2. ✅ Preference persisted in `localStorage` (`bbs-color-mode`); survives refresh (boot script avoids flash)  
3. ✅ Theme toggle on Home, Auth, Owner AppBar, Billing AppBar, and Settings → Appearance  
4. ✅ Surfaces adapt: layouts, cards, tables, charts, landing/auth backgrounds  

**Prior next question:** Should I start Sprint 19?

---

## Appendix — Sprint 17 outcome (prior)

1. ✅ Shared shell tokens (`DRAWER_WIDTH`, `MainContent`) + theme overflow / toolbar consistency  
2. ✅ Bills history + Billing home aligned to `PageShell` / `FilterBar` / `TableCard` / `EmptyState`  
3. ✅ Profile + auth forms match Settings card/spacing patterns; AuthLayout owns page titles  
4. ✅ Owner/Billing chrome aligned (no AppBar quick-link clutter; account-menu icons; Change Password in menu only)  
5. ✅ Removed AI duplicate hero + Categories redundant hierarchy block; Settings `hotel*` → `business*`  

**Prior next question:** Should I start Sprint 18?

---

## Appendix — Sprint 16 outcome (prior)

1. ✅ Shared plan constants: **₹550 / month** Business Billing Plan  
2. ✅ Landing `#pricing` shows plan includes + Register / Login / Contact CTAs  
3. ✅ Owner Settings → Subscription section (email/call support; no checkout)  
4. ✅ Explicit “no online payment in app” messaging — no fake paid gateway  

**Prior next question:** Should I start Sprint 17?

---

## Appendix — Sprint 15 outcome (prior)

1. ✅ Professional landing at `/` — brand-first full-bleed hero  
2. ✅ Sections: Features, Modules, Businesses, Billing, Reports, AI, Security, Subscription teaser, Contact, 24/7 Support, Footer  
3. ✅ Company block: Prabha Technology Pvt. Ltd. (Pune address, email, phone)  
4. ✅ CTAs: Register Business + Login; no hotel-only positioning  
5. ✅ Sora + Source Sans 3; motion on hero (respects reduced-motion)  

**Prior next question:** Should I start Sprint 16?

---

## Appendix — Sprint 14 outcome (prior)

1. ✅ Decision support: best/slow movers, demand hints, recommendations, observed outlook  
2. ✅ Explicit insufficient-data for empty periods; demand comparison flags missing prior period  
3. ✅ `GET /api/v1/ai/decisions` + enriched `/ai/analysis` `decisions` block  
4. ✅ No fabricated forecasts — outlook/recommendations cite recorded totals only  
5. ✅ Owner UI Decision Support section; tenant isolation tests  

**Prior next question:** Should I start Sprint 15?

---

## Appendix — Sprint 13 outcome (prior)

1. ✅ Owner AI Assistant (`GET /api/v1/ai/analysis`) — today / week / month / custom  
2. ✅ Insights from real tenant sales only: totals, payment mix, top/low items, categories, trends  
3. ✅ Explicit `insufficient_data` when no finalized bills in period  
4. ✅ OWNER-only + tenant isolation; billing users blocked  
5. ✅ Owner UI at `/owner/ai`  

**Prior next question:** Should I start Sprint 14?

---

## Appendix — Sprint 12 outcome (prior)

1. ✅ Verified audited events: item create/edit/deactivate, bill create/cancel, login, password change  
2. ✅ Item activity remains after soft-deactivate; no audit delete endpoints  
3. ✅ Owner-only read; tenant isolation; billing users blocked  
4. ✅ Generic business copy (audit/user conflict messages); UI action filters cleaned  
5. ✅ Expanded `test_audit_logs.py` coverage  

**Prior next question:** Should I start Sprint 13?

---

## Appendix — Sprint 11 outcome (prior)

1. ✅ Daily / weekly / monthly / custom reports with payment filter  
2. ✅ KPIs: sales, bills, avg, cash/online, items sold, discount, GST, cancelled  
3. ✅ Top/low items + category sales (+ exports)  
4. ✅ Generic owner-only messaging (no hotel wording); tenant-scoped  
5. ✅ Excel/CSV/PDF use business-friendly metric labels  

**Prior next question:** Should I start Sprint 12?

---

## Appendix — Sprint 10 outcome (prior)

1. ✅ Dashboard shows Business Name + Business Type chip  
2. ✅ KPIs: sales, bills, average, cash/online (+ counts), cancelled; today/week/month periods  
3. ✅ Owner/Billing shell copy uses Business Billing (not Hotel Billing)  
4. ✅ Owner page subtitles generalized away from hotel-only wording  
5. ✅ Report summary regression covers week/month KPI fields  

**Prior next question:** Should I start Sprint 11?

---

## Appendix — Sprint 9 outcome (prior)

1. ✅ BillItem snapshots preserve name, unit price, and GST after catalog changes  
2. ✅ Unique bill numbers; detail/print/cancel/reprint flows verified  
3. ✅ Receipt branded with Business Name (`receipt__business`; fallback BUSINESS, not HOTEL)  
4. ✅ FSSAI on receipt only for restaurant/hotel (or legacy blank type)  
5. ✅ History UI: status chips, reference search; print payload includes tenant  

**Prior next question:** Should I start Sprint 10?

---

## Appendix — Sprint 8 outcome (prior)

1. ✅ Cash / Online required on New Bill (default Cash); persisted on create  
2. ✅ Visible on history, print, reports, exports, and owner dashboard  
3. ✅ Filters on bill history + reports; invalid filter rejected  
4. ✅ Shared frontend payment helpers; dashboard/report cash & online bill counts  
5. ✅ Regression coverage expanded in `test_billing.py`  

**Prior next question:** Should I start Sprint 9?

---

## Appendix — Sprint 7 outcome (prior)

1. ✅ Cart remove / qty≤0 only affects the in-memory bill cart (catalog items unchanged)  
2. ✅ Discount, GST, and totals remain server-authoritative on generate  
3. ✅ Optional `reference` API/UI (DB column still `table_number`; legacy alias kept)  
4. ✅ History + receipt show Reference / Ref.; receipt fallback brand is BUSINESS  
5. ✅ Billing catalog shows SKU when present; remove-from-cart copy clarified  

**Prior next question:** Should I start Sprint 8?

---

## Appendix — Sprint 6 outcome (prior)

1. ✅ Catalog fields: `sku`, `cost_price`, `stock_quantity` (+ unique SKU per tenant)  
2. ✅ Search by name or SKU; billing users retain create/edit/deactivate  
3. ✅ Owner/billing Items UI updated; generic (non-menu) copy  
4. ✅ Item activity still available after deactivate  
5. ✅ Migration + apply helper + docs update  

**Prior next question:** Should I start Sprint 7?
