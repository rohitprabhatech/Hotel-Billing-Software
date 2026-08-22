# Functional Requirements — Prabha Billing SaaS V2

**Status:** Draft · Documentation phase

---

## FR-REG Registration

1. Public **Register Business** collects business info, **business type** (14 options), owner, credentials, terms.  
2. Creates **PENDING** registration request only.  
3. Master **Approve** creates tenant + owner (+ trial if enabled).  
4. Master **Reject** requires reason; no tenant created.

## FR-AUTH Authentication

1. Business login at `/login`; Master at `/master/login` (footer dot).  
2. JWT includes role; Master has **no** `tenant_id`.  
3. Logout / password change bumps `token_version`.  
4. Invalid credentials return generic failure (no role leak).

## FR-AUTHZ Authorization

1. Owner / Billing User / Manager (target) with permission matrix.  
2. Master APIs require `master_required`.  
3. Billing user item CRUD gated by permissions; Owner sees full item activity/audit.

## FR-TENANT Tenant

1. Every business is a tenant.  
2. All tenant data scoped server-side.  
3. Deactivate blocks login; data retained.  
4. Subscription suspend locks billing (402) while login may remain.

## FR-TYPE Business type

1. Exactly 14 types; codes stable for config.  
2. Type drives enabled modules/features/navigation/dashboard.  
3. Adding a 15th type later should be config + module pack, not rewrite.

## FR-BILL Billing engine

1. Lines: product and/or service.  
2. Qty, unit, price, discount, CGST/SGST/IGST as applicable.  
3. Payments: cash, online, UPI, card, credit, partial, advance.  
4. Returns/refunds as lifecycle extensions.  
5. Stock validation on product lines (no negative unless setting).

## FR-INV Inventory

1. Modes: simple qty, weight, volume, length, area, serial/IMEI, batch/lot, expiry, variants.  
2. Restaurant optional recipe deduction.  
3. Stock movements append-only ledger.

## FR-IND Industry modules

See [industry-modules.md](./industry-modules.md). Each pack adds only industry workflows on top of core.

## FR-RPT Reports

Common sales/payment/expense/GST/outstanding + industry reports.

## FR-NOTIF / FR-AUD Notifications & audit

Configurable rules; append-only audit with old/new snapshots where applicable.

## FR-SUB Subscription

States: PENDING, TRIAL, ACTIVE, EXPIRING, EXPIRED, CANCELLED, SUSPENDED.  
Expiring window (default 5 days) notifies Owner and Master.

## FR-AI / FR-WA AI & WhatsApp

Tenant-scoped insights; invoice/quotation/booking messages via configured WhatsApp.

## FR-UI

Landing markets all 14 industries; professional SaaS UI; dark mode; fix Owner↔Billing nav in UX sprint (documented issue only for now).

## FR-SEC

Input validation, CORS, rate limits, hashed passwords, no secret leakage, backup discipline.
