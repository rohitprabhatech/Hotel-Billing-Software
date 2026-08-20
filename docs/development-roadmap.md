# Development Roadmap — Business Billing SaaS

Software: **Business Billing** · Provider: **Prabha Technology Pvt. Ltd.**  
Stack: Flask + SQLAlchemy + MySQL · React + MUI + Vite · Multi-tenant (`tenant_id`)

**Execution rule (mandatory):** After each sprint → test → report → **STOP** → ask approval before the next. Never auto-start the next sprint.

---

## Phase 1 — Multi-business conversion (COMPLETE)

Sprints **1–22** (2026-08-14) delivered: `business_type`, Register Business, schema/relationships, categories/items/billing/payments, reports, audit, AI, landing v1, subscription info, UI pass, dark mode, docs, E2E guide, security hardening, final QA.

Status table and outcomes: see **Appendix A — Phase 1** at the end of this file.  
Release gate: [`final-qa-report.md`](./final-qa-report.md) · Security: [`security-tenant-audit.md`](./security-tenant-audit.md)

---

## Phase 2 — Landing, Category UX, UI polish, Performance, Testing (COMPLETE)

**Program goal:** Commercial-grade landing + clearer parent-category UX + consistent UI/responsive polish + measured performance work + grocery-focused E2E testing — **without rebuilding the product**.

**Release gate:** [`phase2-final-qa-report.md`](./phase2-final-qa-report.md) (2026-08-14)

### Phase 2 audit summary (2026-08-14) — read-only

#### What already works well

| Area | Current state |
|------|----------------|
| Auth / tenancy | Register Business, JWT + `token_version`, Owner / Billing User RBAC |
| Categories BE | Self-ref `parent_id`, tenant-scoped parent, own-parent + circular blocked, inactive parent blocked, soft `is_active` |
| Categories FE (Owner) | MUI **Autocomplete** parent picker + helper text + hierarchy table indent |
| Items / bills | Soft deactivate; bill line snapshots; cash/online; reference field; cancel/print |
| Reports / AI / Audit | Owner-only; tenant-scoped; AI does not invent empty-period metrics |
| Design system | Shared theme light/dark (`bbs-color-mode`), Owner/Billing shells, PageShell / FilterBar / TableCard |
| Isolation | App-level `tenant_id` on queries; Sprint 21 security fixes (logout revoke, global email uniqueness) |

#### Gaps vs this improvement program

| Gap | Severity | Notes |
|-----|----------|--------|
| Landing looks “product wiki” not commercial SaaS | High | Long stacked sections; Unsplash hero; **no mobile hamburger**; weak conversion hierarchy |
| Company contact outdated | High | `frontend/src/constants/company.js` still Khed-Shivapur / support@prabhatech.in / +91 20 7123 4567 |
| Parent category UX clarity | Medium | Mostly done; tighten helper copy (“Leave empty / No Parent…”), Billing Path column, Items category picker |
| App UI consistency / density | Medium | Not a greenfield redesign — polish spacing, empty/loading states, tables across pages |
| Responsive edge cases | Medium | Landing mobile nav; wide tables rely on horizontal scroll |
| Performance | Medium | Item list serialize N+1 (category/creator); no FE page controls (hard `per_page` caps); eager route imports; categories unpaginated |
| DB edge cases | Low–Med | MySQL UNIQUE + NULL root names; `update_item` may allow inactive category; live DB may lag migrations (`apply_pending_schema.py`) |
| Grocery E2E sample data | Medium | Guide has B3; seed is hotel-centric; need Shree General Store scripted data |
| Docs refresh for Phase 2 outcomes | Medium | Manuals/test guide need contact + landing + UX updates after implementation |

#### Explicit non-goals (unless later approved)

- Payment gateway / checkout  
- Rebuild from scratch / new frameworks  
- Hard-delete financial history  
- Invented AI forecasting beyond recorded data  

---

## Phase 2 sprint strategy

Order adjusted to **actual codebase**: landing + contact first (visible commercial gap), then category UX polish, then DB/performance, then verification sprints, then docs/QA.

| Sprint | Title | Nature |
|--------|-------|--------|
| **P2-1** | Formal Phase 2 audit report + DB relationship checklist | Docs only |
| **P2-2** | Landing / Home redesign + company contact update | Major FE |
| **P2-3** | Registration / login / auth flow verification | Verify + small fixes |
| **P2-4** | Parent Category UX + hierarchy clarity | FE polish (+ BE if gaps) |
| **P2-5** | Database relationship corrections + migrations | Schema harden |
| **P2-6** | Application UI/UX consistency pass | Cross-app polish |
| **P2-7** | Responsive design pass | Breakpoints 320–1440 |
| **P2-8** | Performance / speed optimization | Measured only |
| **P2-9** | Billing + payment method verification | Verify + tests |
| **P2-10** | Reports + dashboard verification | Verify + tests |
| **P2-11** | Audit + item activity verification | Verify + tests |
| **P2-12** | Testing documentation + grocery sample data | Docs + seeds/fixtures |
| **P2-13** | Security + tenant isolation retest | Tests + report delta |
| **P2-14** | Final QA + production readiness | Release gate |

---

## Phase 3 — Operational hardening (COMPLETE)

**Program goal:** Fix production-facing operational gaps (AI crash UX, stock enforcement, in-app notifications, WhatsApp delivery, PDF/stock ops) without rebuilding the product.

**Release gate:** [`phase3-final-qa-report.md`](./phase3-final-qa-report.md) (2026-08-14)

| Sprint | Title | Status |
|--------|-------|--------|
| **P3-1** | AI blank page + stock enforcement + notifications | **COMPLETED** — [`phase3-p3-1-ai-stock-notifications.md`](./phase3-p3-1-ai-stock-notifications.md) |
| **P3-2** | Stock/notification polish + route ErrorBoundary | **COMPLETED** — [`phase3-p3-2-stock-notification-polish.md`](./phase3-p3-2-stock-notification-polish.md) |
| **P3-3** | WhatsApp bill sharing / delivery (Cloud API) | **COMPLETED** — [`phase3-p3-3-whatsapp-bill-delivery.md`](./phase3-p3-3-whatsapp-bill-delivery.md) |
| **P3-4** | WhatsApp delivery polish (history, audit, rate-limit) | **COMPLETED** — [`phase3-p3-4-whatsapp-delivery-polish.md`](./phase3-p3-4-whatsapp-delivery-polish.md) |
| **P3-5** | Bill PDF download + stock adjust + ErrorBoundary | **COMPLETED** — [`phase3-p3-5-pdf-stock-adjust.md`](./phase3-p3-5-pdf-stock-adjust.md) |
| **P3-6** | Phase 3 production gate + residual polish | **COMPLETED** — [`phase3-p3-6-phase3-gate.md`](./phase3-p3-6-phase3-gate.md) · [`phase3-final-qa-report.md`](./phase3-final-qa-report.md) |

---

## Phase 4 — Delivery intelligence (COMPLETE)

**Program goal:** Improve outbound bill delivery visibility (WhatsApp status, future channels) without rebuilding billing.

**Gate:** [`phase4-final-qa-report.md`](./phase4-final-qa-report.md) (148 pytest green at gate; FE build OK)

| Sprint | Title | Status |
|--------|-------|--------|
| **P4-1** | Meta WhatsApp delivery status webhooks | **COMPLETED** — [`phase4-p4-1-whatsapp-webhooks.md`](./phase4-p4-1-whatsapp-webhooks.md) |
| **P4-2** | Failure & webhook ops polish | **COMPLETED** — [`phase4-p4-2-whatsapp-ops-polish.md`](./phase4-p4-2-whatsapp-ops-polish.md) |
| **P4-3** | Failed delivery ops visibility | **COMPLETED** — [`phase4-p4-3-failed-delivery-visibility.md`](./phase4-p4-3-failed-delivery-visibility.md) |
| **P4-4** | WhatsApp delivery analytics KPIs | **COMPLETED** — [`phase4-p4-4-delivery-analytics.md`](./phase4-p4-4-delivery-analytics.md) |
| **P4-5** | Phase 4 production gate + close | **COMPLETED** — [`phase4-p4-5-phase4-gate.md`](./phase4-p4-5-phase4-gate.md) |

---

## Phase 5 — Multi-channel bill reach (COMPLETE)

**Program goal:** Get finalized bills to customers reliably across channels — finish WhatsApp ops UX, then email bill delivery — without inventory/PO or in-app SaaS checkout.

**Gate:** [`phase5-final-qa-report.md`](./phase5-final-qa-report.md) (152 pytest green at gate; FE build OK)

| Sprint | Title | Status |
|--------|-------|--------|
| **P5-1** | List-level WhatsApp retry | **COMPLETED** — [`phase5-p5-1-list-whatsapp-retry.md`](./phase5-p5-1-list-whatsapp-retry.md) |
| **P5-2** | Email PDF bill delivery | **COMPLETED** — [`phase5-p5-2-email-bill-delivery.md`](./phase5-p5-2-email-bill-delivery.md) |
| **P5-3** | Email delivery ops parity | **COMPLETED** — [`phase5-p5-3-email-ops-parity.md`](./phase5-p5-3-email-ops-parity.md) |
| **P5-4** | Phase 5 production gate + close | **COMPLETED** — [`phase5-p5-4-phase5-gate.md`](./phase5-p5-4-phase5-gate.md) |

---

## Phase 6 — Inventory operations (COMPLETE)

**Program goal:** Turn existing stock enforcement into owner-ready inventory ops (movement history, low-stock visibility, receive/adjust) without full PO or multi-warehouse.

**Gate:** [`phase6-final-qa-report.md`](./phase6-final-qa-report.md) (160 pytest green at gate; FE build OK)

| Sprint | Title | Status |
|--------|-------|--------|
| **P6-1** | Stock movement ledger + owner low-stock ops | **COMPLETED** — [`phase6-p6-1-stock-movements.md`](./phase6-p6-1-stock-movements.md) |
| **P6-2** | Receive stock + low-stock ops polish | **COMPLETED** — [`phase6-p6-2-receive-stock.md`](./phase6-p6-2-receive-stock.md) |
| **P6-3** | Inventory health + Phase 6 gate | **COMPLETED** — [`phase6-p6-3-inventory-health-gate.md`](./phase6-p6-3-inventory-health-gate.md) |

---

## Phase 7 — Landing commercial redesign (COMPLETE)

**Program goal:** Premium multi-business Billing SaaS public landing (layout inspired by commercial SaaS references; original Business Billing design — no CRM copy/assets).

**Gate:** [`phase7-final-qa-report.md`](./phase7-final-qa-report.md) (FE build OK at gate)

| Sprint | Title | Status |
|--------|-------|--------|
| **P7-1** | Landing page redesign | **COMPLETED** — [`phase7-p7-1-landing-redesign.md`](./phase7-p7-1-landing-redesign.md) |
| **P7-2** | Landing polish + legal pages + Phase 7 gate | **COMPLETED** — [`phase7-p7-2-landing-polish-gate.md`](./phase7-p7-2-landing-polish-gate.md) |

---

## Phase 8 — Master Admin + SaaS subscription management (COMPLETE)

**Program goal:** Prabha Technology operates the SaaS: Master Admin dashboard, registration approval, configurable trial, DB-backed plans, subscription lifecycle, expiry notifications, and landing pricing from the API — **without rebuilding** Owner/Billing.

**Execution rule:** After each sprint → test → report → **STOP** → wait for approval.

**Non-goals:** Payment-gateway checkout; mixing Master into Owner dashboard; DB reset / hard-delete of financial data.

**Audit:** [`phase8-p8-1-architecture-audit.md`](./phase8-p8-1-architecture-audit.md)

| Sprint | Title | Status |
|--------|-------|--------|
| **P8-1** | Existing architecture audit | **COMPLETED** — [`phase8-p8-1-architecture-audit.md`](./phase8-p8-1-architecture-audit.md) |
| **P8-2** | Master Admin authentication + dashboard foundation | **COMPLETED** — [`phase8-p8-2-master-auth.md`](./phase8-p8-2-master-auth.md) |
| **P8-3** | Business registration approval | **COMPLETED** — [`phase8-p8-3-registration-approval.md`](./phase8-p8-3-registration-approval.md) |
| **P8-4** | Trial management | **COMPLETED** — [`phase8-p8-4-trial-management.md`](./phase8-p8-4-trial-management.md) |
| **P8-5** | Plan management | **COMPLETED** — [`phase8-p8-5-plan-management.md`](./phase8-p8-5-plan-management.md) |
| **P8-6** | Subscription lifecycle + access gate | **COMPLETED** — [`phase8-p8-6-subscription-lifecycle.md`](./phase8-p8-6-subscription-lifecycle.md) |
| **P8-7** | Notifications, email, scheduled expiry checks | **COMPLETED** — [`phase8-p8-7-expiry-notifications.md`](./phase8-p8-7-expiry-notifications.md) |
| **P8-8** | Dynamic landing page pricing | **COMPLETED** — [`phase8-p8-8-dynamic-landing-pricing.md`](./phase8-p8-8-dynamic-landing-pricing.md) |
| **P8-9** | Security + tenant isolation | **COMPLETED** — [`phase8-p8-9-security-isolation.md`](./phase8-p8-9-security-isolation.md) |
| **P8-10** | Testing + documentation gate | **COMPLETED** — [`phase8-p8-10-testing-docs-gate.md`](./phase8-p8-10-testing-docs-gate.md) |

---

## Phase 8 follow-on — Cloud DB + Master ops hardening (**SIGNED OFF**)

**Program goal:** Inspect the existing hosted database without dropping data, close remaining Master Admin gaps, then publish current manuals and the full E2E guide.

**Execution rule:** After each sprint → test → report → **STOP** → wait for “start the next sprint”.

| Sprint | Title | Status |
|--------|-------|--------|
| **1** | Cloud DB audit baseline | **COMPLETED** — [`sprint-1-cloud-db-audit-baseline.md`](./sprint-1-cloud-db-audit-baseline.md) |
| **2** | Schema diff + upgrade plan | **COMPLETED** — [`sprint-2-cloud-schema-diff-and-upgrade-plan.md`](./sprint-2-cloud-schema-diff-and-upgrade-plan.md) |
| **3** | Live DB inspection tooling | **COMPLETED** — [`sprint-3-live-db-inspection-tooling.md`](./sprint-3-live-db-inspection-tooling.md) |
| **4** | Master login UX | **COMPLETED** — [`sprint-4-master-login-ux.md`](./sprint-4-master-login-ux.md) |
| **5** | Master business lifecycle + platform audit | **COMPLETED** — [`sprint-5-master-lifecycle-platform-audit.md`](./sprint-5-master-lifecycle-platform-audit.md) |
| **6** | Documentation + E2E testing guide | **COMPLETED** — [`sprint-6-docs-e2e-guide.md`](./sprint-6-docs-e2e-guide.md) |
| **7** | Master dashboard query performance | **COMPLETED** — [`sprint-7-master-query-performance.md`](./sprint-7-master-query-performance.md) |
| **8** | Live database inspect | **COMPLETED** — [`sprint-8-live-database-inspect.md`](./sprint-8-live-database-inspect.md) |
| **9** | Non-destructive live schema apply | **COMPLETED** — [`sprint-9-live-schema-apply.md`](./sprint-9-live-schema-apply.md) |
| **10** | Live platform readiness + Master Admin bootstrap | **COMPLETED** — [`sprint-10-master-bootstrap.md`](./sprint-10-master-bootstrap.md) |
| **11** | Phase 8 Alembic coverage | **COMPLETED** — [`sprint-11-phase8-alembic.md`](./sprint-11-phase8-alembic.md) |
| **12** | Final verification / signoff | **COMPLETED** — [`sprint-12-final-verification.md`](./sprint-12-final-verification.md) |
| **13** | Status-filtered business list pagination | **COMPLETED** — [`sprint-13-status-filter-pagination.md`](./sprint-13-status-filter-pagination.md) |
| **14** | Master registration-request list pagination | **COMPLETED** — [`sprint-14-registration-pagination.md`](./sprint-14-registration-pagination.md) |
| **15** | Master dashboard KPI filters | **COMPLETED** — [`sprint-15-dashboard-kpi-filters.md`](./sprint-15-dashboard-kpi-filters.md) |

**Open ops step:** seed the first Master Admin. Use `.\.venv\Scripts\python.exe scripts\seed_master_admin.py` after setting `MASTER_ADMIN_EMAIL` / `MASTER_ADMIN_PASSWORD` (do not commit). Live `master_admins` remains empty until that succeeds (`check_platform_ready.py` exit 1 = schema OK, seed required).

---

## Phase 2 sprint details

### Sprint P2-1 — Audit report + DB checklist

**Goal:** Publish formal Phase 2 audit artifact; live checklist of FKs/indexes vs `02_schema.sql`.

**Tasks:**
- Document FE/BE/DB findings (this audit)
- Table-by-table relationship checklist (Tenant→Users/Categories/Items/Bills/Audit; Category self-ref; Bill→BillItems)
- Note env drift risk (`business_type` / catalog columns via `apply_pending_schema.py`)

**Deliverable:** `docs/phase2-architecture-audit.md` (or extend this roadmap §audit)  
**Out of scope:** Code changes  
**Acceptance:** Written audit + checklist committed  

---

### Sprint P2-2 — Landing redesign + company info

**Goal:** Commercial SaaS landing; correct Prabha Technology contacts everywhere.

**Tasks:**
- Redesign `/` — professional hierarchy (Navbar → Hero → Value → Features → Business types → Billing → Reports → AI → Security → Why us → Pricing ₹550 → Support → Contact → Footer)
- Navbar: brand left; Features / Modules / AI Insights / Pricing / About / Contact; Login + Register; **mobile hamburger**
- Avoid AI-template look (no purple gradients, pill spam, glass overload, huge headings)
- Update `company.js` (and any other surfaces) to:

  - Address: B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune, Maharashtra – 411041  
  - Email: prabha.technology.01@gmail.com  
  - Phone: 8767865572  

- Hero: “Smart Billing and Business Management” — not “Hotel Billing Software”
- Pricing informational only (no gateway)
- Dark mode must still work on landing

**Acceptance:** Mobile nav works; contacts correct site-wide; visual review vs commercial SaaS bar  

---

### Sprint P2-3 — Auth / registration verification

**Goal:** Prove Register Business + login + verify + password flows against current APIs.

**Tasks:** Smoke/register/login/reset; business_type persistence; legacy `register-hotel` alias still safe  
**Acceptance:** Documented pass/fail + fixes only if regressions found  

---

### Sprint P2-4 — Parent Category UX

**Goal:** Owners clearly understand Main vs Sub category.

**Tasks:**
- Form copy: Category Name, Description, Parent Category  
- Helper: *“Leave this as No Parent / Main Category to create a main category. Select a category to create a subcategory.”*  
- Keep/improve Autocomplete (searchable); hierarchy visual on list (Food → Veg / Non-Veg style indent)  
- Confirm BE validations still block cycles / cross-tenant / inactive parent  

**Acceptance:** Manual create Food → Veg/Non-Veg works without confusion; invalid parent rejected by API  

---

### Sprint P2-5 — Database relationships + migrations

**Goal:** Close remaining schema/relationship edges without destructive resets.

**Tasks:**
- Reconcile live DB vs `sql/02_schema.sql` + Alembic / `apply_pending_schema.py`  
- Root-name uniqueness strategy (MySQL NULL unique quirk)  
- Fix `update_item` inactive-category inconsistency if confirmed  
- Update `docs/database-design.md` / relationships doc  

**Acceptance:** Migration/script path works on clean + existing DB; tests green  

---

### Sprint P2-6 — Application UI/UX consistency

**Goal:** One product, one visual system across owner/billing/auth (not a full rewrite).

**Tasks:** Spacing/typography/buttons/tables/dialogs/empty/loading/error states; align Items category picker with hierarchy labels  
**Avoid:** Random padding, mismatched controls, oversized cards  
**Acceptance:** Spot-check all key routes for consistency  

---

### Sprint P2-7 — Responsive design

**Goal:** Usable layouts at 320 / 375 / 768 / 1024 / 1280 / 1440.

**Tasks:** Landing, auth, dashboards, tables, dialogs, sidebar; no overlap/clip/horizontal page scroll (table scroll OK inside TableCard)  
**Acceptance:** Checklist signed for those breakpoints  

---

### Sprint P2-8 — Performance

**Goal:** Fix **measured** bottlenecks only.

**Tasks:**
- Item list N+1 (eager load category/creator)  
- FE pagination or load-more for items/bills where needed  
- Route-level code splitting for heavy pages  
- Index review for report/dashboard hot paths  
- Billing catalog search remains fast with many items  

**Acceptance:** Before/after notes (query counts or perceived load); no functional regressions  

---

### Sprint P2-9 — Billing + payment verification

**Goal:** Cash/Online, remove-from-cart, totals, print/cancel still correct.

**Acceptance:** Guided tests with sample bills; Biscuits remove does not delete catalog item  

---

### Sprint P2-10 — Reports + dashboard verification

**Goal:** Today/week/month totals match manual calc on sample bills.

**Acceptance:** Documented reconciliation for sample data  

---

### Sprint P2-11 — Audit + item activity verification

**Goal:** LOGIN / CREATE_BILL / item create-edit-deactivate visible to Owner after Billing User actions.

**Acceptance:** History survives deactivate  

---

### Sprint P2-12 — Testing docs + sample data

**Goal:** Step-by-step manual with **exact** entries.

**Sample business:**
- Shree General Store · Grocery Store  
- Owner: Rajesh Patil · owner@example.com  
- Billing: Amit Sharma · billing@example.com  

**Categories:** Grocery → Rice, Pulses; Beverages → Cold Drinks  
**Items:** Rice 5kg ₹450; Dal 1kg ₹140; Cold Drink 750ml ₹50; Biscuits ₹30  
**Bills:** Cash + Online mixes; remove Biscuits before finalize  

Update: `test-business-billing-guide.md`, user/owner/billing manuals as needed  

---

### Sprint P2-13 — Security + tenant isolation retest

**Goal:** Business A ↛ Business B for categories/items/bills/reports/users/audit/activity.

**Acceptance:** Automated + manual isolation matrix green; delta vs Sprint 21 report  

---

### Sprint P2-14 — Final QA

**Goal:** Phase 2 release gate.

**Acceptance:** Signed QA note; landing + UX + perf + tests documented  

---

## Phase 2 status

| Item | Status |
|------|--------|
| Phase 2 audit (roadmap summary) | ✅ Completed (2026-08-14) |
| Sprint P2-1 — Formal audit report + DB checklist | ✅ Completed (2026-08-14) |
| Sprint P2-2 — Landing redesign + company contacts | ✅ Completed (2026-08-14) |
| Sprint P2-3 — Auth / registration verification | ✅ Completed (2026-08-14) |
| Sprint P2-4 — Parent Category UX | ✅ Completed (2026-08-14) |
| Sprint P2-5 — Database relationships + migrations | ✅ Completed (2026-08-14) |
| Sprint P2-6 — Application UI/UX consistency | ✅ Completed (2026-08-14) |
| Sprint P2-7 — Responsive design | ✅ Completed (2026-08-14) |
| Sprint P2-8 — Performance | ✅ Completed (2026-08-14) |
| Sprint P2-9 — Billing + payment verification | ✅ Completed (2026-08-14) |
| Sprint P2-10 — Reports + dashboard verification | ✅ Completed (2026-08-14) |
| Sprint P2-11 — Audit + item activity verification | ✅ Completed (2026-08-14) |
| Sprint P2-12 — Testing docs + sample data | ✅ Completed (2026-08-14) |
| Sprint P2-13 — Security + tenant isolation retest | ✅ Completed (2026-08-14) |
| Sprint P2-14 — Final QA | ✅ Completed (2026-08-14) |
| Deliverable (P2-1) | [`phase2-architecture-audit.md`](./phase2-architecture-audit.md) |
| Deliverable (P2-3) | [`phase2-p2-3-auth-verification.md`](./phase2-p2-3-auth-verification.md) |
| Deliverable (P2-7) | [`phase2-p2-7-responsive-checklist.md`](./phase2-p2-7-responsive-checklist.md) |
| Deliverable (P2-8) | [`phase2-p2-8-performance.md`](./phase2-p2-8-performance.md) |
| Deliverable (P2-9) | [`phase2-p2-9-billing-verification.md`](./phase2-p2-9-billing-verification.md) |
| Deliverable (P2-10) | [`phase2-p2-10-reports-verification.md`](./phase2-p2-10-reports-verification.md) |
| Deliverable (P2-11) | [`phase2-p2-11-audit-verification.md`](./phase2-p2-11-audit-verification.md) |
| Deliverable (P2-12) | [`phase2-p2-12-testing-sample-data.md`](./phase2-p2-12-testing-sample-data.md) |
| Deliverable (P2-13) | [`phase2-p2-13-security-isolation.md`](./phase2-p2-13-security-isolation.md) |
| Deliverable (P2-14) | [`phase2-final-qa-report.md`](./phase2-final-qa-report.md) |
| Phase 2 program | ✅ Complete — staging pilot recommended |

---

## Phase 2 Sprint P2-1 outcome

1. ✅ Formal Phase 2 architecture audit published  
2. ✅ Database relationship / FK / index checklist for live-DB verification  
3. ✅ Gaps prioritized for landing, contacts, category UX, UI, perf, grocery E2E  
4. ✅ No application code changes in this sprint  

---

## Phase 2 Sprint P2-2 outcome

1. ✅ Commercial landing redesign (`HomePage.jsx`) — brand-first hero, section hierarchy, ₹550 pricing, no gateway  
2. ✅ Sticky navbar with Features / Modules / AI Insights / Pricing / About / Contact + Login / Register  
3. ✅ Mobile hamburger drawer  
4. ✅ Company contacts updated in `company.js`, manuals, and docs README (Pune Shreya Business Hub / new email / phone)  
5. ✅ Dark mode–compatible palette (teal ink gradients; no Unsplash stock hero)  

---

## Phase 2 Sprint P2-3 outcome

1. ✅ Auth pytest suites green (16 passed: login, register, verify, reset, change-password, isolation)  
2. ✅ Live API smoke: register grocery → block login → verify → login → `business_type` on `/me` and `/tenants/me`  
3. ✅ Legacy `POST /auth/register-hotel` still works; invalid type → 400  
4. ✅ Forgot + reset password round-trip OK; FE routes wired to current APIs  
5. ✅ No regressions found — **no app code changes**  
6. ✅ Report: [`phase2-p2-3-auth-verification.md`](./phase2-p2-3-auth-verification.md)  

---

## Phase 2 Sprint P2-4 outcome

1. ✅ Owner Categories dialog: Category Name / Description / Parent Category + required helper copy for Main vs Sub  
2. ✅ Searchable Parent Autocomplete with hierarchy indentation + live “main / subcategory under …” hint  
3. ✅ List shows tree indent, Main/Sub chips, path as `Food → Veg` style  
4. ✅ Billing categories list aligned (Type column + tree indent)  
5. ✅ BE validations reconfirmed via pytest (`test_categories_items` — parent/circular/cross-tenant/inactive parent)  
6. ✅ Frontend production build OK  

---

## Phase 2 Sprint P2-5 outcome

1. ✅ Root-name uniqueness: generated `categories.parent_key` (VIRTUAL `IFNULL(parent_id,'')`) + unique `(tenant_id, parent_key, name)`  
2. ✅ `02_schema.sql`, Alembic `20260814_category_parent_key`, `apply_category_parent_key.py` wired into `apply_pending_schema.py`  
3. ✅ Applied successfully on local MySQL (STORED ALTER rejected with 1215; VIRTUAL used)  
4. ✅ `ItemService.update_item` now rejects inactive category (aligned with create)  
5. ✅ Docs updated: `database-design.md`, `database-relationships.md`, audit hole closed  
6. ✅ Pytest green (`test_categories_items` + `test_schema_relationships`, including new duplicate-root + inactive-move cases)  

---

## Phase 2 Sprint P2-6 outcome

1. ✅ Shared `CategoryHierarchyAutocomplete` + hierarchy utils — Items filter/dialog + Categories parent picker  
2. ✅ Item rows show `category_hierarchy_path` (API field added)  
3. ✅ Shared `LoadingBlock` / `FormSection`; Bills empty-state sibling pattern; Billing categories chips aligned  
4. ✅ Filter control widths via `filterControlSx` / `filterControlWideSx` on Items  
5. ✅ Profile / Settings / Change Password use shared form section chrome  
6. ✅ Frontend build + category/item pytest green  

---

## Phase 2 Sprint P2-7 outcome

1. ✅ Landing: hamburger through tablet; hero/support CTAs mobile-safe; footer/business grids stepped  
2. ✅ AppBar: role chip hidden on `xs`; tighter gutters (Owner + Billing)  
3. ✅ Auth: top-align on small screens; full-width submit buttons  
4. ✅ New Bill catalog stacks on `xs`; dialogs wrap; TableCard denser on phone  
5. ✅ KPI/chart polish for drawer + narrow viewports  
6. ✅ Checklist: [`phase2-p2-7-responsive-checklist.md`](./phase2-p2-7-responsive-checklist.md)  

---

## Phase 2 Sprint P2-8 outcome

1. ✅ Item list N+1 fixed (`joinedload` category/creator + category map for hierarchy path)  
2. ✅ Items + bills tables paginated (25/page) with `PaginationBar`  
3. ✅ Route-level `React.lazy` code splitting (main chunk ~325KB vs prior ~1.1MB)  
4. ✅ Billing catalog search debounced (250ms); report index `ix_bills_tenant_status_created_at`  
5. ✅ Notes: [`phase2-p2-8-performance.md`](./phase2-p2-8-performance.md)  

---

## Phase 2 Sprint P2-9 outcome

1. ✅ Billing suites green (cash/online, server totals, reference, print/cancel)  
2. ✅ Biscuits cart-omit test: catalog item remains active when omitted from bill  
3. ✅ Online + discount totals confirmed with nearest-rupee round-off  
4. ✅ FE remove-from-cart is cart-state only (tooltip already documents)  
5. ✅ Report: [`phase2-p2-9-billing-verification.md`](./phase2-p2-9-billing-verification.md) — **no app code changes**  

---

## Phase 2 Sprint P2-10 outcome

1. ✅ Sample bills (cash + online + cancelled) reconciled to hand calc for today / this_week / this_month  
2. ✅ Cancelled excluded from `total_sales`; cash/online split + average bill match  
3. ✅ Billing home `/bills/today-summary` aligns with report today metrics  
4. ✅ Existing `test_reports.py` still green; new `test_p2_10_reports_reconciliation.py`  
5. ✅ Report: [`phase2-p2-10-reports-verification.md`](./phase2-p2-10-reports-verification.md) — **no app code changes**  

---

## Phase 2 Sprint P2-11 outcome

1. ✅ Owner sees Billing User `LOGIN` and `CREATE_BILL` in audit logs  
2. ✅ Item create / update / deactivate visible via Item Activity (`entity_type=ITEM`)  
3. ✅ Soft-deactivate keeps audit snapshots (name + reason); billing still 403 on audit API  
4. ✅ Suites green: `test_p2_11_audit_item_activity` + `test_audit_logs` + `test_billing_item_management` (18 passed)  
5. ✅ Report: [`phase2-p2-11-audit-verification.md`](./phase2-p2-11-audit-verification.md) — **no app code changes**  

---

## Phase 2 Sprint P2-12 outcome

1. ✅ Canonical sample: Shree General Store · Rajesh / Amit · grocery hierarchy + four items  
2. ✅ Exact Script G (Cash ₹620, Online ₹105 after Biscuits cart-remove) in test guide  
3. ✅ Owner / Billing / User manuals reference the practice sample  
4. ✅ Docs index links P2-10…P2-12 notes  
5. ✅ Report: [`phase2-p2-12-testing-sample-data.md`](./phase2-p2-12-testing-sample-data.md) — **docs only**  

---

## Phase 2 Sprint P2-13 outcome

1. ✅ Isolation matrix green: categories / items / bills / reports / users / audit / activity  
2. ✅ Sprint 21 hardening reconfirmed (logout/deactivate revoke, email uniqueness, audit immutable)  
3. ✅ No new Critical/High regressions vs [`security-tenant-audit.md`](./security-tenant-audit.md)  
4. ✅ Residual follow-ups unchanged (non-blocking)  
5. ✅ Report: [`phase2-p2-13-security-isolation.md`](./phase2-p2-13-security-isolation.md) — **no app code changes**  

---

## Phase 2 Sprint P2-14 outcome

1. ✅ Full backend pytest green (**119** passed)  
2. ✅ Frontend production build green (lazy chunks retained)  
3. ✅ Landing + UX + perf + verification sprints rolled into signed gate  
4. ✅ Staging pilot = Script G (Shree General Store) + schema apply reminder  
5. ✅ Report: [`phase2-final-qa-report.md`](./phase2-final-qa-report.md) — **Phase 2 release gate signed**  

**Phase 2 complete.** Product owner: approve staging pilot, then production cutover.

---

## Terminology (unchanged)

| Prefer | Avoid |
|--------|--------|
| Business | Hotel (as product default) |
| Register Business | Register Hotel |
| Business Dashboard | Hotel Dashboard |

Hotel remains a **valid business type**, not the product name.

---

## Appendix A — Phase 1 status (sprints 1–22)

| Item | Status |
|------|--------|
| Phase 0 + Sprints 1–22 | ✅ Completed (2026-08-14) |
| Program | Multi-business conversion complete; staging pilot recommended |

Prior detailed outcomes remain in git history of this file / [`final-qa-report.md`](./final-qa-report.md).
