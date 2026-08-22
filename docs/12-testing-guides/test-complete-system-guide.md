# Test Complete System Guide

_Derived from prior guides; historical originals archived._

# Business Billing — Complete E2E Testing Guide

**Audience:** Developers, QA, UAT  
**Stack:** Flask + React multi-tenant SaaS  
**Terminology:** Prefer **Business** (Hotel is a valid *business type* only)  
**Last updated:** 2026-08-18 (Sprint 6 — Master Admin + SaaS E2E)  
**Supersedes naming in:** [test-hotel-billing-guide.md](./test-hotel-billing-guide.md)

Fill **Actual** / **Pass?** during manual runs. Automated suite (API):

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```

---

## A. Primary sample pack — Shree General Store (P2-12)

Use these **exact** values for the guided grocery walkthrough (Script G below).

### A.1 Register Business (Owner)

| Field | Exact value |
|-------|-------------|
| Business name | `Shree General Store` |
| Business type | `Grocery Store` (`grocery_store`) |
| Owner name | `Rajesh Patil` |
| Owner email | `owner@example.com` |
| Password / confirm | `Owner@12345` |
| Mobile (optional) | `9876543210` |
| Address (optional) | `12 Market Road, Pune` |

After register → request is **PENDING**. Master Admin must **Approve**. Then login as Owner (email is already verified on approve). Do **not** expect immediate login.

### A.2 Billing User (Owner → Users)

| Field | Exact value |
|-------|-------------|
| Name | `Amit Sharma` |
| Email | `billing@example.com` |
| Password | `Billing@12345` |
| Role | Billing User |

Login as Billing User for counter steps.

### A.3 Categories (Owner → Categories)

Create in this order (Parent = **No Parent / Main Category** unless noted):

| # | Name | Parent |
|---|------|--------|
| 1 | `Grocery` | — (main) |
| 2 | `Rice` | Grocery |
| 3 | `Pulses` | Grocery |
| 4 | `Beverages` | — (main) |
| 5 | `Cold Drinks` | Beverages |

### A.4 Items (Owner or Billing → Items)

Use **5% GST** for all sample lines (keeps totals predictable).

| Name | Category path | Price (₹) | GST % |
|------|---------------|-----------|-------|
| `Rice 5kg` | Grocery › Rice | `450` | `5` |
| `Dal 1kg` | Grocery › Pulses | `140` | `5` |
| `Cold Drink 750ml` | Beverages › Cold Drinks | `50` | `5` |
| `Biscuits` | Grocery (main) or Pulses | `30` | `5` |

### A.5 Expected bill math (server rules)

- Line GST after discount; **grand total rounds to nearest ₹**.  
- Examples (no discount):

| Cart | Pre-round | Grand |
|------|-----------|-------|
| Rice 5kg × 1 | 450 + 22.50 = 472.50 | **₹473** |
| Dal 1kg × 1 | 140 + 7.00 = 147.00 | **₹147** |
| Rice + Dal (one bill) | 590 + 29.50 = 619.50 | **₹620** |
| Cold Drink × 2 | 100 + 5.00 = 105.00 | **₹105** |
| Biscuits × 1 | 30 + 1.50 = 31.50 | **₹32** |

---

## B. Multi-business isolation pack (optional)

Create additional businesses with **different owner emails** when testing tenant isolation (P2-13).

| Code | Business name | Type | Categories | Items | Reference style |
|------|---------------|------|------------|-------|-----------------|
| **B1** | Cafe Bloom | `restaurant` | Beverages › Hot · Food › Snacks | Masala Chai ₹40 (5% GST), Samosa ₹25 | Table `T-04` |
| **B2** | Style Hub | `clothing_store` | Men › Shirts · Women › Tops | Oxford Shirt ₹899 (SKU `OXF-M-L`), Cotton Top ₹649 | Token `TK-118` |
| **B3** | Daily Mart | `grocery_store` | Staples · Packaged | Toor Dal 1kg ₹160 (stock 40), Oil 1L ₹180 | Counter `C-2` |

**Isolation rule:** A bill / item / report from B1 must never appear when logged into B2 or B3.

**Demo seed (optional local):** `owner@hotela.com` / `Owner@12345`, `billing@hotela.com` / `Billing@12345` (treat as Business A).

---

## C. Automated coverage map

| Area | Pytest modules (primary) |
|------|--------------------------|
| Registration / verify / password | `test_saas_registration_auth.py`, `test_p8_3_registration_approval.py`, `test_sprint20_gaps.py`, `test_auth.py` |
| Master Admin auth / lifecycle / audit | `test_p8_2_master_auth.py`, `test_sprint5_master_lifecycle_audit.py` |
| Trial / plans / subscription gate / expiry / public pricing | `test_p8_4_trial_management.py`, `test_p8_5_plan_management.py`, `test_p8_6_subscription_lifecycle.py`, `test_p8_7_expiry_notifications.py`, `test_p8_8_public_pricing.py` |
| Roles / inactive / suspended | `test_auth.py`, `test_production_readiness.py`, `test_sprint20_gaps.py` |
| Tenant isolation | `test_tenant_isolation.py`, `test_reports.py`, `test_ai_assistant.py`, `test_audit_logs.py` |
| Categories / parents / items / SKU | `test_categories_items.py`, `test_billing_item_management.py`, `test_sprint20_gaps.py` |
| Billing totals / cash-online / reference | `test_billing.py`, `test_money.py`, `test_p2_9_billing_verification.py` |
| Cart validation (empty / qty≤0 / merge / discount cap) | `test_sprint20_gaps.py` |
| Print / cancel / history | `test_print_cancel.py` |
| Reports / export / RBAC | `test_reports.py`, `test_p2_10_reports_reconciliation.py` |
| Audit / item activity | `test_audit_logs.py`, `test_p2_11_audit_item_activity.py`, `test_billing_item_management.py` |
| AI analysis / decisions | `test_ai_assistant.py` |
| Tenant settings fields | `test_sprint20_gaps.py`, `test_tenant_isolation.py` |

**Manual-only (no API):** dark mode persistence, landing/subscription UI (no Pay button), footer Master dot, browser print layout, responsive chrome, cart remove *before* finalize (client cart).

---

## D. Prerequisites

| Check | Expected | Pass? |
|-------|----------|-------|
| Schema applied / migrations | App starts cleanly. Existing DBs: inspect then `apply_pending_schema.py`. **Never** `02_schema.sql` on live data | |
| `GET /api/v1/health` | success | |
| Frontend `npm run dev` | `/` loads Business Billing | |
| `pytest -q` | All green | |

---

## 1. Public, registration, auth

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 1.1 | Open `/` | Brand hero; Register Business + Login; Features → Pricing from **public plans API** (not a hard-coded-only ₹550 if other public plans exist) | Manual | |
| 1.2 | Dark mode toggle → refresh | Preference kept (`bbs-color-mode`) | Manual | |
| 1.3 | Register **Shree General Store** with §A.1 values, accept Terms | Request **PENDING**; **login fails** until Master approves | Manual | |
| 1.3b | Master approves request | Tenant + OWNER created; owner can login | Manual+Auto | |
| 1.4 | Register invalid type `spaceship` | Rejected | Auto | |
| 1.5 | Register omit `business_type` | Defaults to `other` | Auto | |
| 1.6 | Forgot / reset password | Completes; can login with new password | Partial | |
| 1.7 | Change password | Old JWT rejected; must re-login | Auto | |
| 1.8 | Deactivate tenant (Master) → call `/auth/me` with old JWT; try login | Authenticated call 401 “suspended”; login 401 | Auto | |

---

## 2. Roles & isolation

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 2.1 | Owner creates Amit Sharma (§A.2) | User logs into `/billing` only | Manual | |
| 2.2 | Billing User opens Reports / AI / Audit / Users | Blocked (UI + API 403) | Auto (API) | |
| 2.3 | Owner A opens Owner B bill id | 404/403 | Auto | |
| 2.4 | Same SKU on two businesses | Both allowed (tenant-scoped) | Auto | |
| 2.5 | Forged `tenant_id` in create-user body | Ignored; user stays on caller tenant | Auto | |

---

## 3. Categories & items

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 3.1 | Create §A.3 hierarchy | Paths show Grocery › Rice, Beverages › Cold Drinks | Manual | |
| 3.2 | Create §A.4 items | Searchable on New Bill | Manual | |
| 3.3 | Soft-deactivate Biscuits | Hidden from active catalog; old bills keep snapshot | Auto+Manual | |
| 3.4 | Item Activity | Create/edit/deactivate attributed to Amit / Rajesh | Auto+Manual | |
| 3.5 | Billing User cannot create category | 403 / no UI action | Partial | |

---

## 4. Billing (counter)

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 4.1 | Cart: add Biscuits then remove before finalize | Line gone; catalog Biscuits still active | Manual | |
| 4.2 | API qty 0 / empty cart | 400 | Auto | |
| 4.3 | Duplicate item lines in one POST | Merged quantities | Auto | |
| 4.4 | Discount + GST | Server totals correct | Auto | |
| 4.5 | Discount > subtotal | 400 | Auto | |
| 4.6 | Reference `C-1` | Stored; history/print show **Reference** | Manual | |
| 4.7 | Cash then Online bills (§G) | Labels + report filters | Manual+Auto | |
| 4.8 | Print / reprint | Count increments; payload has business + lines | Auto+Manual | |
| 4.9 | Cancel with reason | CANCELLED; audit + history; **tracked stock restored** | Auto | |
| 4.10 | Change price after bill | Historical snapshot unchanged | Auto | |
| 4.11 | Stock: Rice stock 10, bill qty 5 then qty 6 | Second bill **rejected** `INSUFFICIENT_STOCK`; stock stays 5 | Auto | |
| 4.12 | Multi-item: A=10 B=3; bill A5+B5 | Entire bill rejected; no partial deduct | Auto | |
| 4.13 | Sell to 0 then qty 1 | Out-of-stock notification; bill rejected | Auto | |

---

## 5. Owner analytics

| # | Steps | Expected | Auto? | Pass? |
|---|-------|----------|-------|-------|
| 5.1 | Dashboard today / week / month | KPIs for Shree General Store only | Auto+Manual | |
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
| 6.2 | FSSAI hint for restaurant vs grocery | Contextual only | Manual | |
| 6.3 | Subscription | Current trial/plan/status; Contact/email; **no Pay / checkout** | Manual | |
| 6.4 | Appearance toggle | Persists across pages + refresh | Manual | |
| 6.5 | Email change request | Verification before switch | Partial | |

---

## 7. End-to-end scripts (manual)

### Script G — Shree General Store (P2-12 primary · ~45–60 min)

Fill **Pass?** as you go.

| Step | Exact action | Expected | Pass? |
|------|--------------|----------|-------|
| G1 | Register + **Master approve** + login as `owner@example.com` / `Owner@12345` | Owner Dashboard shows **Shree General Store** | |
| G2 | Settings → confirm business type Grocery Store | Type matches | |
| G3 | Categories: create §A.3 exactly | Hierarchy visible | |
| G4 | Items: create §A.4 exactly (5% GST) | Four items in catalog | |
| G5 | Users → create Amit Sharma §A.2 | User appears active | |
| G6 | Logout → login `billing@example.com` / `Billing@12345` | Lands on Billing | |
| G7 | **Bill Cash:** New Bill → add `Rice 5kg` ×1 + `Dal 1kg` ×1 → Reference `C-1` → **Cash** → generate | Grand **₹620**; payment Cash | |
| G8 | Print bill | Receipt shows Shree General Store + lines + Reference `C-1` | |
| G8b | Owner Settings → WhatsApp (mock/dev) → save config → Billing send WhatsApp on bill with mobile `91` + test number | Bill stays same number; delivery Sent; print still works | |
| G8c | Force fail token / disconnect → Send WhatsApp | Clear error; bill FINALIZED; Retry + Print available | |
| G9 | **Bill Online + remove Biscuits:** add `Cold Drink 750ml` ×2 + `Biscuits` ×1 → **remove Biscuits** from cart → Reference `C-2` → **Online** → generate | Grand **₹105**; only cold drinks on bill; **Biscuits still in Items catalog** | |
| G10 | Owner login → Reports today | Cash + online sales include ₹620 and ₹105; cancelled count 0 | |
| G11 | Owner → Audit | `LOGIN` (Amit), `CREATE_BILL` for both bills | |
| G12 | Billing → soft-deactivate `Biscuits` (reason `Out of stock`) | Hidden from active New Bill catalog | |
| G13 | Owner → Item Activity | `ITEM_CREATED` / `ITEM_DEACTIVATED` for Biscuits remain | |
| G14 | Dark mode toggle → refresh | Preference kept | |
| G15 | Subscription settings | Trial or plan info; **no Pay button** | |

### Script B — Cross-tenant (20 min)

1. With two businesses (e.g. Shree General Store + Cafe Bloom) each having ≥1 bill, switch accounts.  
2. Confirm catalogs and reports never mix.  
3. Attempt to open the other business’s bill URL/id → denied.

### Script C — Smoke (15 min)

Landing → Login → New Bill cash → Print → Reports summary → Dark toggle → Logout.

---

## 9. Master Admin, landing, SaaS lifecycle (Sprint 6)

Use a **local Master Admin** created with `backend/scripts/seed_master_admin.py` (do not commit the password). Sign in only at `/master/login`.

Fill **Actual** / **Pass?** on each row.

### 9.1 Landing page

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| L1 | Open `/` | Navbar, hero, features, pricing, register, login | | |
| L2 | Open `/privacy` and `/terms` | Legal pages load | | |
| L3 | Footer | Contact + legal links. **No** “Master Login” / “Admin Login” text | | |
| L4 | Scroll to footer bottom-right | Subtle low-contrast **dot** only | | |
| L5 | Click the dot | `/master/login` opens | | |

### 9.2 Master login

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| M1 | `/master/login` | Heading Prabha Technology / Administration; Email, Password, Sign In | | |
| M2 | No Register / Forgot Password on this page | Those links absent | | |
| M3 | Wrong password | Generic invalid credentials | | |
| M4 | Owner email/password on Master login | Generic invalid credentials; **no** Master console | | |
| M5 | Valid Master credentials | Master Dashboard | | |
| M6 | Logged-out visit to `/master/dashboard` | Redirect to `/master/login` | | |
| M7 | Owner JWT → `GET /api/v1/master/dashboard/summary` | **403** | | |

### 9.3 Registration (exact SaaS sample)

| Field | Exact value |
|-------|-------------|
| Business name | `Shree Family Restaurant` |
| Business type | Restaurant (`restaurant`) |
| Owner | `Rahul Patil` |
| Email | `rahul.test@example.com` |
| Mobile | `9876543210` |
| Password | Use a local-only secure password (min 8 chars) |

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| R1 | Landing → Register Your Business | Form loads | | |
| R2 | Fill §9.3, accept Terms + Privacy, submit | Success; status PENDING; **no JWT** | | |
| R3 | Login as Rahul before approve | Blocked (pending approval) | | |
| R4 | Master → Registration requests | Row for Shree Family Restaurant | | |
| R5 | Open detail | No password / password_hash | | |
| R6 | Reject with reason shorter than 8 chars | 400 | | |
| R7 | Approve (or reject with a long reason, then re-register and approve) | Tenant ACTIVE; owner can login | | |
| R8 | Owner login | Dashboard shows **Shree Family Restaurant**; tenant data matches the form | | |

### 9.4 Plans (landing)

| Field | Exact value |
|-------|-------------|
| Plan name | `Professional` |
| Price | `999` |
| Billing | Monthly |
| Features | Billing, Stock, Reports, AI Insights, WhatsApp |
| Public / Active | Yes |

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| P1 | Master → Plans → create Professional ₹999 | Saved | | |
| P2 | Open landing pricing | **Professional ₹999/month** appears without a code change | | |
| P3 | Deactivate the plan | Landing no longer offers it as a public plan | | |
| P4 | Existing subscription `price_at_purchase` | Unchanged if you only edited catalog price | | |

### 9.5 Trial defaults (new approvals only)

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| T1 | Trial settings: ON, **15** days | Saved | | |
| T2 | Approve a new test business | Trial remaining = **15** days | | |
| T3 | Change trial days to **30** | Saved | | |
| T4 | Approve a **second** new business | New trial = **30** days | | |
| T5 | Re-check the first business | Still **15** days remaining window (not rewritten to 30) | | |
| T6 | Trial OFF, approve a third business | Owner can login; bills **402** until plan assign / trial start | | |

### 9.6 Activate / deactivate / suspend

Use any approved test tenant (not production).

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| B1 | Master → Deactivate | Login blocked; users/bills/items still in DB | | |
| B2 | Activate | Login works again | | |
| B3 | Suspend | Login + profile OK; `/bills` **402** | | |
| B4 | Resume | Billing works if the period is still valid | | |
| B5 | Master Audit log | BUSINESS_DEACTIVATED / ACTIVATED / SUSPENDED / UNSUSPENDED present; no password fields | | |

### 9.7 Expiry

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| E1 | Set a test subscription to end within `expiry_warning_days` (default 5) | Status EXPIRING | | |
| E2 | Run expiry job (`POST /master/jobs/expiry-check` or CLI) | Owner in-app + email notice; Master bell; **one** notice per period | | |
| E3 | Move end date to the past; run job again | EXPIRED; Owner notice; billing **402**; login still works | | |
| E4 | Run the job again on the same period | No duplicate EXPIRING/EXPIRED notice | | |

### 9.8 Tenant isolation (API + UI)

Create:

- Business A: **Shree Family Restaurant** (distinct items/categories/bills)
- Business B: **Smart Fashion Store** (`clothing_store`) with different catalog and at least one bill

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| I1 | Login A: list items, categories, bills, reports, notifications, audit, `/auth/me` subscription | Only A | | |
| I2 | A opens B’s item/bill/user id via API | 404/403 | | |
| I3 | Repeat as B | Only B | | |
| I4 | Forged `tenant_id` in a create body | Ignored | | |

### 9.9 Cloud migration checklist (ops — do not execute blindly)

| # | Steps | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| C1 | Verified backup of live DB | Location + timestamp recorded | Sprint 9: `backend/backups/20260818T113408Z-u583892242_HotelBillingDB.json` (11:34:08 UTC, gitignored) | Pass |
| C2 | `inspect_database_schema.py --json-out` | Read-only report; Phase 8 tables listed present/missing | Sprint 8 baseline: all 8 Phase 8 **missing**. Post Sprint 9+: all present. See sprint-8 / sprint-9 JSON | Pass |
| C3 | Confirm **not** running `02_schema.sql` | Destructive file unused on live | Still unused | Pass |
| C4 | After approval: `apply_pending_schema.py` | Creates missing tables only; tenant/bill counts stable | Sprint 9: 15→23 app tables; tenants/users/bills 1/1/2 unchanged | Pass |
| C5 | Re-inspect | `platform_audit_logs` and other Phase 8 tables exist | Sprint 9 / 12: all 8 Phase 8 tables present; 24 objects with `alembic_version` | Pass |
| C6 | `stamp_alembic_head.py` | `alembic_version = 20260818_phase8_saas` | Sprint 11 | Pass |
| C7 | `check_platform_ready.py` | Schema OK; reports `master_admins` count | Exit 1 while seed pending (`master_admins: 0`) | Open ops |
| C8 | `seed_master_admin.py` via **python.exe** | `Created master admin: …` then ready exit 0 | Run only after `MASTER_ADMIN_*` set in `.env` | Open ops |

---

## 10. Exit criteria

| Criterion | Met? |
|-----------|------|
| `pytest -q` green on CI/local | Yes (follow-on Sprint 15: 241 passed) |
| Script G executed once with **exact** §A entries (after Master approve) | |
| Scripts L/M/R/P/T/B/E/I executed or auto-covered | |
| Guide documents pending registration + Master footer dot + no Pay button | Yes |
| Owner / Billing / User / Master manuals match current architecture | Yes |
| Backup/inspect-before-migrate documented | Yes |
| Hosted Phase 8 schema + Alembic stamp | Yes (Sprints 9–12) |
| Live Master Admin seeded | Open ops (`master_admins` may still be 0) |
| No hotel-only product language in this guide | Yes |

---

## Related docs

- [user-manual.md](./user-manual.md) · [owner-manual.md](./owner-manual.md) · [billing-user-manual.md](./billing-user-manual.md) · [master-admin-manual.md](./master-admin-manual.md)  
- [registration-approval-flow.md](./registration-approval-flow.md) · [subscription-management.md](./subscription-management.md) · [trial-management.md](./trial-management.md) · [plan-management.md](./plan-management.md)  
- [tenant-isolation.md](./tenant-isolation.md) · [security-architecture.md](./security-architecture.md) · [backup-and-recovery.md](./backup-and-recovery.md)  
- [phase2-p2-12-testing-sample-data.md](./phase2-p2-12-testing-sample-data.md)  
- [api-documentation.md](./api-documentation.md) · [deployment-guide.md](./deployment-guide.md)
