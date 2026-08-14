# Business Billing — Complete E2E Testing Guide

**Audience:** Developers, QA, UAT  
**Stack:** Flask + React multi-tenant SaaS  
**Terminology:** Prefer **Business** (Hotel is a valid *business type* only)  
**Last updated:** 2026-08-14 (Sprint 20)  
**Supersedes naming in:** [test-hotel-billing-guide.md](./test-hotel-billing-guide.md)

Fill **Actual** / **Pass?** during manual runs. Automated suite (API):

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```

---

## A. Multi-business sample pack (use these)

Create three isolated businesses (Register Business or seed + second registrations). Use **different owner emails**.

| Code | Business name | Type | Categories | Items | Reference style |
|------|---------------|------|------------|-------|-----------------|
| **B1** | Cafe Bloom | `restaurant` | Beverages › Hot · Food › Snacks | Masala Chai ₹40 (5% GST), Samosa ₹25 | Table `T-04` |
| **B2** | Style Hub | `clothing_store` | Men › Shirts · Women › Tops | Oxford Shirt ₹899 (SKU `OXF-M-L`), Cotton Top ₹649 | Token `TK-118` |
| **B3** | Daily Mart | `grocery_store` | Staples · Packaged | Toor Dal 1kg ₹160 (stock 40), Oil 1L ₹180 | Counter `C-2` |

**Isolation rule:** A bill / item / report from B1 must never appear when logged into B2 or B3.

**Demo seed (optional local):** `owner@hotela.com` / `Owner@12345`, `billing@hotela.com` / `Billing@12345` (treat as Business A).

---

## B. Automated coverage map

| Area | Pytest modules (primary) |
|------|--------------------------|
| Registration / verify / password | `test_saas_registration_auth.py`, `test_sprint20_gaps.py` |
| Roles / inactive / suspended | `test_auth.py`, `test_production_readiness.py`, `test_sprint20_gaps.py` |
| Tenant isolation | `test_tenant_isolation.py`, `test_reports.py`, `test_ai_assistant.py`, `test_audit_logs.py` |
| Categories / parents / items / SKU | `test_categories_items.py`, `test_billing_item_management.py`, `test_sprint20_gaps.py` |
| Billing totals / cash-online / reference | `test_billing.py`, `test_money.py` |
| Cart validation (empty / qty≤0 / merge / discount cap) | `test_sprint20_gaps.py` |
| Print / cancel / history | `test_print_cancel.py` |
| Reports / export / RBAC | `test_reports.py`, `test_sprint20_gaps.py` |
| Audit | `test_audit_logs.py` |
| AI analysis / decisions | `test_ai_assistant.py` |
| Tenant settings fields | `test_sprint20_gaps.py`, `test_tenant_isolation.py` |

**Manual-only (no API):** dark mode persistence, landing/subscription UI (no Pay button), browser print layout, responsive chrome, cart remove *before* finalize (client cart).

---

## C. Prerequisites

| Check | Expected | Pass? |
|-------|----------|-------|
| Schema applied / migrations | App starts cleanly | |
| `GET /api/v1/health` | success | |
| Frontend `npm run dev` | `/` loads Business Billing | |
| `pytest -q` | All green | |

---

## 1. Public, registration, auth

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 1.1 | Open `/` | Brand hero; Register Business + Login; Features → Pricing ₹550 | Manual | |
| 1.2 | Dark mode toggle → refresh | Preference kept (`bbs-color-mode`) | Manual | |
| 1.3 | Register **B2** `clothing_store` | Tenant + OWNER; verify email then login | Partial | |
| 1.4 | Register invalid type `spaceship` | Rejected | Auto | |
| 1.5 | Register omit `business_type` | Defaults to `other` | Auto | |
| 1.6 | Forgot / reset password | Completes; can login with new password | Partial | |
| 1.7 | Change password | Old JWT rejected; must re-login | Auto | |
| 1.8 | Suspend tenant → call `/auth/me` with old JWT; try login | Authenticated call 401 “suspended”; login 401 | Auto | |

---

## 2. Roles & isolation (B1 vs B2)

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 2.1 | Owner creates Billing User on B1 | User logs into `/billing` only | Partial | |
| 2.2 | Billing User opens Reports / AI / Audit / Users | Blocked (UI + API 403) | Auto (API) | |
| 2.3 | B1 owner opens B2 bill id | 404/403 | Auto | |
| 2.4 | Same SKU on B1 and B2 | Both allowed (tenant-scoped) | Auto | |
| 2.5 | Forged `tenant_id` in create-user body | Ignored; user stays on caller tenant | Auto | |

---

## 3. Categories & items

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 3.1 | B1: parent + child category | Path / indent visible | Auto | |
| 3.2 | B2: Men › Shirts + Oxford Shirt with SKU/stock | Searchable on New Bill | Manual+Auto | |
| 3.3 | Soft-deactivate item | Hidden from active catalog; old bills keep snapshot | Auto | |
| 3.4 | Item Activity | Create/edit/deactivate attributed | Auto | |
| 3.5 | Billing User cannot create category | 403 / no UI action | Partial | |

---

## 4. Billing (counter)

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 4.1 | Cart: remove line / qty ≤ 0 in UI | Line gone before finalize | Manual | |
| 4.2 | API qty 0 / empty cart | 400 | Auto | |
| 4.3 | Duplicate item lines in one POST | Merged quantities | Auto | |
| 4.4 | Discount + GST | Server totals correct | Auto | |
| 4.5 | Discount > subtotal | 400 | Auto | |
| 4.6 | Reference `T-04` / `TK-118` | Stored; history/print show **Reference** | Auto+Manual | |
| 4.7 | Cash then Online bills | Labels + report filters | Auto | |
| 4.8 | Print / reprint | Count increments; payload has business + lines | Auto+Manual layout | |
| 4.9 | Cancel with reason | CANCELLED; audit + history | Auto | |
| 4.10 | Change price after bill | Historical snapshot unchanged | Auto | |

---

## 5. Owner analytics

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 5.1 | Dashboard today / week / month | KPIs for **this** business only | Auto+Manual | |
| 5.2 | Weekly report + top/low items | Sections populated when sales exist | Auto | |
| 5.3 | Export CSV / XLSX / PDF | Downloads; human labels | Auto (xlsx) + Manual | |
| 5.4 | AI with sales | Metrics + decisions from real totals | Auto | |
| 5.5 | AI empty period | Insufficient-data messaging | Auto | |
| 5.6 | Audit LOGIN / CREATE_BILL / PASSWORD_CHANGED | Visible when actions occurred | Auto | |

---

## 6. Settings, subscription, theme

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 6.1 | Settings → Business Information | Name, address, GST, prefix persist | Auto+Manual | |
| 6.2 | FSSAI hint for restaurant vs clothing | Contextual only | Manual | |
| 6.3 | Subscription | ₹550/mo; Contact/email; **no Pay / checkout** | Manual | |
| 6.4 | Appearance toggle | Persists across pages + refresh | Manual | |
| 6.5 | Email change request | Verification before switch | Partial | |

---

## 7. End-to-end scripts (manual)

### Script A — Cafe Bloom (45–60 min)

1. Register/login B1 Owner → set business info → add categories/items.  
2. Create Billing User → login as Billing → New Bill (Cash, ref `T-04`) → print.  
3. Second bill Online → cancel one with reason.  
4. Owner: Dashboard, Reports export, AI analyze, Audit filter CANCEL.  
5. Toggle dark mode → refresh → still dark.  
6. Confirm Subscription section has no payment button.

### Script B — Cross-tenant (20 min)

1. With B1 and B2 both having ≥1 bill, switch accounts.  
2. Confirm catalogs and reports never mix.  
3. Attempt to open the other business’s bill URL/id → denied.

### Script C — Smoke (15 min)

Landing → Login → New Bill cash → Print → Reports summary → Dark toggle → Logout.

---

## 8. Exit criteria (Sprint 20)

| Criterion | Met? |
|-----------|------|
| `pytest -q` green on CI/local | |
| Scripts A+C executed once on staging/local | |
| Guide uses multi-business sample data (B1–B3) | Yes |
| Dark mode + subscription verified manually | |
| No hotel-only product language in this guide | Yes |

---

## Related docs

- [user-manual.md](./user-manual.md) · [owner-manual.md](./owner-manual.md) · [billing-user-manual.md](./billing-user-manual.md)  
- [api-documentation.md](./api-documentation.md) · [deployment-guide.md](./deployment-guide.md)  
