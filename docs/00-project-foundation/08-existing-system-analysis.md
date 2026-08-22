# Existing System Analysis — Prabha Billing SaaS V2

**Branch:** `rs/feature/billingV2`  
**Phase:** Documentation only — no code or database changes.  
**Date:** 2026-08-20

---

## 1. What the product is today

| Field | Current value |
|-------|----------------|
| Repo folder | `Hotel-Billing-Software` (legacy name) |
| Product name in UI | **Business Billing** |
| Provider | Prabha Technology Pvt. Ltd. |
| Stack | Flask + SQLAlchemy + MySQL/MariaDB · React + Vite + MUI |
| Tenancy | Shared DB, `tenant_id` scoping; JWT never trusts client `tenant_id` |
| Roles | `OWNER`, `BILLING_USER`, platform `MASTER_ADMIN` |
| Application tables | **23** (+ `alembic_version` on live) |
| Alembic head (live) | `20260818_phase8_saas` |

The product already operates as a **multi-tenant SaaS** with Master Admin, registration approval, plans, trial, WhatsApp/email bill delivery, stock movements, AI insights, audit, and notifications.

---

## 2. Reusable foundation (keep and extend)

| Area | Status | Location (examples) |
|------|--------|---------------------|
| Master Admin auth + console | Implemented | `master_admins`, `/master/*`, footer-dot login |
| Registration approval | Implemented | `registration_requests` |
| Plans + public pricing | Implemented | `subscription_plans`, `GET /public/plans` |
| Trial + subscription gate | Implemented | `platform_settings`, `subscriptions`, lockout UI |
| Billing (cash/online) | Implemented | `bills`, `bill_items` |
| Categories (hierarchy + `parent_key`) | Implemented | `categories` |
| Items + soft deactivate | Implemented | `items` |
| Stock qty + movements | Implemented | `stock_movements`, adjust/receive |
| Tenant audit + platform audit | Implemented | `audit_logs`, `platform_audit_logs` |
| Notifications (tenant + platform) | Implemented | `notifications`, `platform_notifications` |
| WhatsApp + email delivery | Implemented | `bill_deliveries`, webhooks |
| AI analysis (tenant-scoped) | Implemented | `/ai/analysis`, `/ai/decisions` |
| Reports / export | Implemented | `/reports/*` |
| PDF / print | Implemented | bill PDF + print route |

**Principle for V2:** extend this core. Do not rebuild auth, tenancy, or Master Admin from scratch.

---

## 3. Current business types (canonical — BIZ-01)

Codes in `backend/app/constants/business_types.py` (**exactly 14**):

`hotel_restaurant`, `cafe_tea`, `grocery_kirana`, `clothing`, `mobile`, `hardware`, `bakery_sweet`, `stationery`, `electronics`, `furniture`, `building_material`, `book_store`, `wholesale`, `travel_agency`

- Used for registration / profile labeling and FSSAI hints for food types (`hotel_restaurant`, `cafe_tea`, `bakery_sweet`).  
- Module/feature flags still planned (BIZ-02).  
- **Medical Store is not present** and remains **out of scope**.  
- Legacy codes (`hotel`, `restaurant`, `kirana_store`, …) map via Alembic `20260820_biz01_business_types`.

---

## 4. Gaps vs V2 multi-industry vision

| Capability | Today | V2 target |
|------------|-------|-----------|
| Industry modules | None | 14 module packs |
| Module / feature flags | None | `BusinessType` → enabled modules |
| Customers (CRM) | Fields on bill only | Customer master |
| Suppliers / purchase / expenses | Missing | Common core |
| Product vs service lines | Product-centric | Product + service + mixed |
| Variants (size/color), IMEI, batch/expiry | Missing / partial stock only | Inventory engine |
| Restaurant tables / KOT / kitchen | Missing (`table_number` = reference) | Restaurant module |
| Manager role | Missing | Optional business role |
| Configurable plan limits (users/products) | Soft / manual | Documented limits model |
| Online SaaS payment gateway | Not in app | Separated from customer payments; still offline/contact unless later approved |
| Owner ↔ Billing navigation | Dual shells; return via “Owner Dashboard” only | UX redesign sprint |

---

## 5. Documented UI issues (do not fix in this phase)

1. **Owner ↔ Billing dual-shell:** Choosing Billing unmounts `OwnerLayout` and mounts `BillingLayout`. Owner loses Owner sidebar (Reports, AI, Users, Settings) until using **Owner Dashboard** in Billing drawer/menu.  
2. Dual “Dashboard” labels for Owner inside Billing shell.  
3. Shared `ItemsPage` under `/owner/items` and `/billing/items` can confuse context.  
4. Legacy names: `table_number` vs UI `reference`; `register-hotel` alias; repo/DB “Hotel” naming.  
5. Parent category UX: hierarchy exists (`parent_id` / `parent_key`) but create/manage UX should be professionalized (select-only feel).  
6. Landing still markets multi-business well; must list **all 14** V2 industries (no Medical).

---

## 6. Database safety snapshot

- Hosted DB has been upgraded via **helpers + stamp**, not `02_schema.sql`.  
- `master_admins` may still be **0** until seed with `python.exe scripts/seed_master_admin.py`.  
- V2 conceptual tables in `database-architecture.md` are **design only** until approved sprints.

---

## 7. Recommendation

| Decision | Rationale |
|----------|-----------|
| Extend, don’t rewrite | Auth, Master, trial, bills, stock, WhatsApp, AI are production-ready |
| Introduce industry config layer | Avoid 14 separate apps |
| Sequence common engines first | Billing + inventory + customers before deep industry packs |
| Keep Medical Store out | Explicit product exclusion |

---

## 8. Files consulted (non-exhaustive)

- `frontend/src/constants/company.js`, `routes/paths.js`, `layouts/*`  
- `backend/app/constants/business_types.py`, `models/*`, `routes/__init__.py`  
- `docs/database-design.md`, `docs/api-documentation.md`, `docs/development-roadmap.md`
