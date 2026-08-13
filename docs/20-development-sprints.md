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

## Sprint 2 — Project Foundation

### Tasks

- Scaffold Flask backend (app factory, config, extensions, folders)
- Scaffold React frontend (Vite or CRA, MUI, router, axios)
- MySQL connection + SQLAlchemy + Flask-Migrate
- `.env.example` files
- Standard API response envelope + error handlers
- Health endpoint
- Basic theme + empty layouts

### Acceptance Criteria

- [ ] Backend starts and `/api/v1/health` works
- [ ] Frontend starts and shows placeholder shell
- [ ] Migrations infrastructure ready
- [ ] CORS and env-based config wired

---

## Sprint 3 — Authentication & Multi-Tenancy

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

- [ ] Both roles can login
- [ ] Protected routes reject missing/invalid JWT
- [ ] BILLING_USER blocked from owner-only APIs
- [ ] Cross-tenant access tests fail closed

---

## Sprint 4 — Categories & Items

### Tasks

- Category CRUD + activate/deactivate
- Item CRUD + price/GST + status
- Validation + audit for item/price/GST changes
- Owner UI for categories/items
- Billing catalog list/search (active only)

### Acceptance Criteria

- [ ] Owner manages categories/items without hard-coded lists
- [ ] Deactivated items excluded from billing search
- [ ] Price/GST changes audited

---

## Sprint 5 — Billing

### Tasks

- Billing UI cart: search, add, qty, remove, clear, discount
- POST finalize bill with server Decimal math
- Bill number counter + unique constraint
- Bill + bill_items snapshots in transaction
- CREATE_BILL audit

### Acceptance Criteria

- [ ] Totals match server rules
- [ ] Concurrent bills get unique numbers
- [ ] Historical snapshot retained after price change
- [ ] No trust of client totals

---

## Sprint 6 — Printing & Bill History

### Tasks

- `BillPreview` / `PrintableReceipt`
- 58mm/80mm print CSS
- Print/reprint + audit + printed_count
- Bill history/search
- Cancel bill with reason + audit

### Acceptance Criteria

- [ ] Receipt uses tenant header fields dynamically
- [ ] Print view excludes app chrome
- [ ] Cancel retains record and reason for owner
- [ ] No hard delete of bills

---

## Sprint 7 — Owner Dashboard & Reports

### Tasks

- Owner dashboard cards + comparisons
- Period reports (day/week/month/custom)
- Item-wise / day-wise data
- Charts
- Excel/CSV/(PDF) export + EXPORT_REPORT audit

### Acceptance Criteria

- [ ] Metrics match DB for sample data
- [ ] Exports tenant-scoped with sensible filenames
- [ ] Billing User cannot access report APIs

---

## Sprint 8 — Audit & Fraud Monitoring

### Tasks

- Owner audit log list + filters + detail drawer
- Activity alerts (cancellations, discounts, reprints, price changes)
- Ensure coverage of required action types

### Acceptance Criteria

- [ ] Owner can filter by user/action/date/bill
- [ ] Cancel detail shows who/when/why/amount
- [ ] Alerts visible without accusatory wording
- [ ] No audit delete API

---

## Sprint 9 — Testing & Production Readiness

### Tasks

- Full regression per [18-testing-strategy.md](./18-testing-strategy.md)
- Security review checklist
- Seed/onboarding docs for new tenants
- Performance smoke on billing path
- Deployment notes verification

### Acceptance Criteria

- [ ] Isolation, billing, GST, cancel, audit, export tests pass
- [ ] No known critical security gaps from checklist
- [ ] App ready for staging pilot with one hotel tenant

---

## Suggested Order of Implementation Sessions

```text
Sprint 1 (docs) → Sprint 2 (foundation) → Sprint 3 (auth/tenant)
→ Sprint 4 (catalog) → Sprint 5 (billing) → Sprint 6 (print/history)
→ Sprint 7 (reports) → Sprint 8 (audit) → Sprint 9 (hardening)
```

## Next Action After Sprint 1 Acceptance

Begin **Sprint 2 — Project Foundation** only after stakeholder confirmation that documentation is accepted (or proceed when user requests Sprint 2).
