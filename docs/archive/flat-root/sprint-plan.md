# Sprint Plan — Prabha Billing SaaS V2

**Branch:** `rs/feature/billingV2`  
**Rule:** Documentation approved first → then **one sprint at a time**. After each sprint: test → report → **STOP** → wait for “start the next sprint”.  
**Safety:** No coding until this plan is approved. No DB changes without backup + sprint authorization.

**Refined after existing-system analysis:** Sprints reuse Master Admin, registration, plans, trial, bills, stock, WhatsApp, AI already shipped in Phase 8.

---

## Sprint 0 — Existing Project Audit

| Field | Content |
|-------|---------|
| Objective | Freeze understanding of current SaaS baseline |
| Dependencies | None |
| Backend | Read-only analysis |
| Frontend | Read-only analysis |
| Database | Inspect-only; no mutate |
| Docs | [existing-system-analysis.md](./existing-system-analysis.md) |
| Acceptance | Gaps vs V2 listed; reusable assets listed; Medical excluded |
| DoD | Analysis published; no code/DB changes |
| Risks | Stale hotel-era docs confuse readers — mark historical |

**Status:** Complete in documentation phase.

---

## Sprint 1 — Product & Multi-Business Architecture

| Field | Content |
|-------|---------|
| Objective | Approve Common Core + Industry Module architecture and 14-type matrix |
| Dependencies | Sprint 0 |
| Backend/Frontend/DB | Design only unless tiny config stubs approved later |
| API | Document module bootstrap contract |
| Testing | N/A (docs) |
| Docs | architecture, business-types, common-core, industry-modules |
| Files expected | Docs only (this phase) |
| Acceptance | 14 types finalized; Medical absent; enablement chain agreed |
| DoD | Stakeholder sign-off on architecture.md |
| Risks | Over-scoping industry packs before core engines |

---

## Sprint 2 — Business Type Config Layer (first code sprint after approval)

| Field | Content |
|-------|---------|
| Objective | Persist BusinessType catalog + module/feature flags; map registration to type |
| Dependencies | Sprint 1 approval |
| Backend | Models/services for BusinessType, Module, Feature, mappings; migrate **from** current string `business_type` carefully |
| Frontend | Register dropdown shows 14 labels; bootstrap `/modules/me` |
| Database | Additive tables only after backup; no drops |
| API | `GET /tenants/business-types` enriched; session module list |
| Testing | Types list; unknown type rejected; isolation unchanged |
| Acceptance | New registration stores canonical type; nav can hide disabled modules |
| DoD | Pytest + docs; Medical not in list |
| Risks | Breaking existing tenants’ type codes — need mapping table |

---

## Sprint 3 — AuthZ Permissions + Manager Role

| Field | Content |
|-------|---------|
| Objective | Permission matrix; optional MANAGER role; billing-user item permissions explicit |
| Dependencies | Sprint 2 |
| Backend | permissions seed; guards |
| Frontend | Hide actions by permission |
| Testing | Owner sees item activity after billing-user edits |
| Acceptance | RBAC documented behavior matches API |
| Risks | Over-restricting existing BILLING_USER item access |

---

## Sprint 4 — Common Billing Engine Extensions

| Field | Content |
|-------|---------|
| Objective | Product/service lines; payment methods UPI/card/credit/partial/advance; payment records |
| Dependencies | Sprint 3 |
| Backend | BillingEngine service; payment entities |
| Frontend | Bill UI payment options |
| Testing | Mixed invoice; insufficient stock still blocked |
| Acceptance | One engine serves product and service lines |
| Risks | Migrating existing bills.payment_method |

---

## Sprint 5 — Inventory Engine Extensions

| Field | Content |
|-------|---------|
| Objective | Units, batch/lot/expiry, variants foundation, negative-stock setting |
| Dependencies | Sprint 4 |
| Backend | InventoryEngine; extend stock_movements |
| Frontend | Unit/batch fields where enabled |
| Testing | Concurrent sell; expiry filter |
| Acceptance | Generic modes work without industry UI yet |
| Risks | Performance on serial-heavy tenants |

---

## Sprint 6 — Customers + Suppliers + Purchase + Expense

| Field | Content |
|-------|---------|
| Objective | CRM and procurement core |
| Dependencies | Sprint 5 |
| Backend/Frontend | CRUD modules; bill link to customer |
| Testing | Isolation T-ISO on new tables |
| Acceptance | Customer credit foundation for grocery/wholesale later |
| Risks | Scope creep into full accounting |

---

## Sprint 7 — Reports + Notifications + Audit Hardening

| Field | Content |
|-------|---------|
| Objective | New report types; rule-driven notifications; audit coverage for new entities |
| Dependencies | Sprint 6 |
| Acceptance | Low-stock and subscription notices remain; new entity audits appear |
| Risks | Notification noise |

---

## Sprint 8 — Type-Aware Dashboards + Nav UX

| Field | Content |
|-------|---------|
| Objective | Dashboard widgets by type; **fix Owner↔Billing return navigation** |
| Dependencies | Sprint 2+ |
| Frontend | Widget registry; shell UX fix |
| Acceptance | Owner can return to Owner Dashboard reliably; restaurant vs grocery widgets differ |
| Risks | Layout regression |

---

## Sprint 9 — Restaurant / Cafe Pack

| Field | Content |
|-------|---------|
| Objective | Tables (Available/Occupied/Reserved), Order → KOT → Kitchen → Billing; optional recipe deduction |
| Dependencies | Sprint 4–5, 8 |
| Backend | `/restaurant/*` `/cafe/*` |
| Frontend | modules/restaurant, cafe |
| Testing | Full workflow acceptance from prompt §6–7 |
| DoD | Industry docs + tests |
| Risks | Complex concurrency on tables |

---

## Sprint 10 — Grocery / Stationery Pack

| Field | Content |
|-------|---------|
| Objective | Fast POS, barcode, units, credit/udhari, expiry alerts |
| Dependencies | Sprint 5–6 |
| Acceptance | Insufficient stock message with available qty |
| Risks | Barcode hardware variance |

---

## Sprint 11 — Clothing / Mobile Pack

| Field | Content |
|-------|---------|
| Objective | Size/color/brand variants; IMEI/serial; exchange/return basics |
| Dependencies | Sprint 5 |
| Acceptance | Size-wise stock; IMEI unique per tenant |
| Risks | Variant SKU explosion |

---

## Sprint 12 — Hardware / Building Material Pack

| Field | Content |
|-------|---------|
| Objective | Multi-unit, length/weight/area, quotations, challan, credit |
| Dependencies | Sprint 5–6 |
| Acceptance | Example pipe qty×price invoice |
| Risks | Unit conversion errors |

---

## Sprint 13 — Bakery / Electronics / Furniture Pack

| Field | Content |
|-------|---------|
| Objective | Production/batch/cake orders; serial/warranty/repair; custom furniture + delivery |
| Dependencies | Sprint 5–6 |
| Risks | Wide pack — split if needed mid-sprint |

---

## Sprint 14 — Books / Wholesale Pack

| Field | Content |
|-------|---------|
| Objective | ISBN metadata; wholesale pricing; warehouses; PO/SO; outstanding |
| Dependencies | Sprint 5–6 |
| Risks | Warehouse complexity |

---

## Sprint 15 — Travel Agency Pack

| Field | Content |
|-------|---------|
| Objective | Packages, bookings, advances, itinerary, commission; service-first billing |
| Dependencies | Sprint 4, 6 |
| Acceptance | Travel billing documented as service-centric |
| Risks | Document storage PII |

---

## Sprint 16 — AI Broadening

| Field | Content |
|-------|---------|
| Objective | Industry-aware insights using real tenant aggregates only |
| Dependencies | Industry data from prior packs |
| Acceptance | No cross-tenant leakage; no invented KPIs |

---

## Sprint 17 — WhatsApp / Print / PDF Polish

| Field | Content |
|-------|---------|
| Objective | Templates for quote/booking/payment; professional invoice layouts per type |
| Dependencies | Billing engine |
| Acceptance | Send bill when printer unavailable |

---

## Sprint 18 — Landing + Marketing (14 industries)

| Field | Content |
|-------|---------|
| Objective | Landing shows all 14; no Medical; dynamic plans; professional UX |
| Dependencies | Sprint 2 |
| Acceptance | Brand-first, responsive, dark mode |

---

## Sprint 19 — Security + Performance Pass

| Field | Content |
|-------|---------|
| Objective | Isolation retest; indexes; rate limit storage; secret audit |
| Acceptance | T-ISO green on all tenant tables |

---

## Sprint 20 — Production Readiness / Deployment

| Field | Content |
|-------|---------|
| Objective | Deploy checklist, backup drill, Master seed verified, runbooks |
| Acceptance | check_platform_ready + docs signed |

---

## Execution protocol (mandatory)

1. Complete sprint tasks.  
2. Run pytest (`FLASK_ENV=testing`, project venv) and frontend build as needed.  
3. Verify API + UI + DB for touched features.  
4. Update docs.  
5. Report changed files, tests, issues, acceptance.  
6. **STOP** and ask: “Should I start the next sprint?”

Do **not** auto-start the next sprint.

---

## Out of program

Medical Store module · Unapproved DROP/DELETE on production · Blind `02_schema.sql` on live DB
