# 20 — Development Sprints

## Rules

- Work **one sprint at a time**
- Do **not** generate the entire application in one step
- After each sprint: Implement → Test → Fix → Verify acceptance → Next sprint
- Sprint 1 is documentation only (this folder)

---

## Sprint 1 — Documentation & Architecture ✅ (Current)

### Deliverables

All files under `docs/`:

- Project overview, functional & non-functional requirements
- System, multi-tenant, frontend, backend architecture
- Roles & permissions
- Database design + ERD
- API contracts
- AuthZ design
- Billing, printing, reporting, audit workflows
- Security, testing, deployment, sprint plan

### Acceptance Criteria

- [x] All 20 documents exist
- [x] Only two roles documented
- [x] Tenant isolation strategy defined
- [x] No hard-delete of financial records in design
- [x] Backend-authoritative billing documented
- [x] Receipt printing requirements captured
- [x] Sprint plan ready for implementation

### Status

**Complete when documentation reviewed.** No application feature code in this sprint.

---

## Sprint 2 — Project Foundation ✅

### Tasks

- Scaffold Flask backend (app factory, config, extensions, folders)
- Scaffold React frontend (Vite, MUI, router, axios)
- MySQL connection + SQLAlchemy + Flask-Migrate
- `.env.example` files
- Standard API response envelope + error handlers
- Health endpoint
- Basic theme + empty layouts

### Acceptance Criteria

- [x] Backend starts and `/api/v1/health` works
- [x] Frontend starts and shows placeholder shell
- [x] Migrations infrastructure ready
- [x] CORS and env-based config wired

---

## Sprint 3 — Authentication & Multi-Tenancy ✅

### Tasks

- Models: tenant, role, user
- Seed roles OWNER / BILLING_USER
- Login/logout/me + JWT
- Password hashing
- Auth middleware + role guards
- Tenant context from JWT
- Owner can manage billing users
- Isolation tests (baseline)

### Acceptance Criteria

- [x] Both roles can login
- [x] Protected routes reject missing/invalid JWT
- [x] BILLING_USER blocked from owner-only APIs
- [x] Cross-tenant access tests fail closed

---

## Sprint 4 — Categories & Items ✅

### Tasks

- Category CRUD + activate/deactivate
- Item CRUD + price/GST + status
- Validation + audit for item/price/GST changes
- Owner UI for categories/items
- Billing catalog list/search (active only)

### Acceptance Criteria

- [x] Owner manages categories/items without hard-coded lists
- [x] Deactivated items excluded from billing search
- [x] Price/GST changes audited

---

## Sprint 5 — Billing ✅

### Tasks

- Billing UI cart: search, add, qty, remove, clear, discount
- POST finalize bill with server Decimal math
- Bill number counter + unique constraint
- Bill + bill_items snapshots in transaction
- CREATE_BILL audit

### Acceptance Criteria

- [x] Totals match server rules
- [x] Concurrent bills get unique numbers
- [x] Historical snapshot retained after price change
- [x] No trust of client totals

---

## Sprint 6 — Printing & Bill History ✅

### Tasks

- `BillPreview` / `PrintableReceipt`
- 58mm/80mm print CSS
- Print/reprint + audit + printed_count
- Bill history/search
- Cancel bill with reason + audit

### Acceptance Criteria

- [x] Receipt uses tenant header fields dynamically
- [x] Print view excludes app chrome
- [x] Cancel retains record and reason for owner
- [x] No hard delete of bills

---

## Sprint 7 — Owner Dashboard & Reports ✅

### Tasks

- Owner dashboard cards + comparisons
- Period reports (day/week/month/custom)
- Item-wise / day-wise data
- Charts
- Excel/CSV/(PDF) export + EXPORT_REPORT audit

### Acceptance Criteria

- [x] Metrics match DB for sample data
- [x] Exports tenant-scoped with sensible filenames
- [x] Billing User cannot access report APIs

---

## Sprint 8 — Audit & Fraud Monitoring ✅

### Tasks

- Owner audit log list + filters + detail drawer
- Activity alerts (cancellations, discounts, reprints, price changes)
- Ensure coverage of required action types

### Acceptance Criteria

- [x] Owner can filter by user/action/date/bill
- [x] Cancel detail shows who/when/why/amount
- [x] Alerts visible without accusatory wording
- [x] No audit delete API

---

## Sprint 9 — Testing & Production Readiness ✅

### Tasks

- Full regression per [18-testing-strategy.md](./18-testing-strategy.md)
- Security review checklist
- Seed/onboarding docs for new tenants
- Performance smoke on billing path
- Deployment notes verification

### Acceptance Criteria

- [x] Isolation, billing, GST, cancel, audit, export tests pass
- [x] No known critical security gaps from checklist
- [x] App ready for staging pilot with one hotel tenant

See [21-production-readiness.md](./21-production-readiness.md).

---

## Suggested Order of Implementation Sessions

```text
Sprint 1 (docs) → Sprint 2 (foundation) → Sprint 3 (auth/tenant)
→ Sprint 4 (catalog) → Sprint 5 (billing) → Sprint 6 (print/history)
→ Sprint 7 (reports) → Sprint 8 (audit) → Sprint 9 (hardening)
```

## Post-Sprint 9

Application is staging-pilot ready. Next work is operational rollout (real hotel onboarding, printer tuning, monitoring) rather than core feature sprints.
