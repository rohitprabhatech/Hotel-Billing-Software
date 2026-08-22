# 07 — Database Design (detailed catalog)

> **Prefer** [database-design.md](./database-design.md) for status and table overview, and [database-relationships.md](./database-relationships.md) for FKs/cascades.  
> **Source of truth:** `backend/sql/02_schema.sql` (23 application tables).  
> This file is the column-level catalog kept current through Phase 8 + follow-on Sprints 1–15.

## Design Principles

1. Tenant isolation via `tenant_id` on all tenant-scoped tables  
2. Decimal money fields (`DECIMAL(12,2)` typical; GST rates `DECIMAL(5,2)`)  
3. Soft status changes for financial records (no hard delete via app)  
4. Historical snapshots on `bill_items`  
5. Proper PKs, FKs, unique constraints, and selective indexes  
6. UTC timestamps (`created_at`, `updated_at`)  
7. Master / platform tables have **no** `tenant_id` (except optional links on audit / registration)

## Table inventory (23)

**Core (15):** `tenants`, `roles`, `users`, `password_reset_tokens`, `email_verification_tokens`, `categories`, `items`, `bill_number_counters`, `bills`, `bill_items`, `notifications`, `tenant_whatsapp_configs`, `bill_deliveries`, `audit_logs`, `stock_movements`

**Phase 8 (8):** `master_admins`, `registration_requests`, `platform_settings`, `subscription_plans`, `subscriptions`, `subscription_notices`, `platform_notifications`, `platform_audit_logs`

Live hosted DBs also have `alembic_version` (stamped `20260818_phase8_saas`).

---

## Tables

### `tenants`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | UUID |
| name | VARCHAR(120) | Display name |
| business_name | VARCHAR(200) | Printed on receipt |
| business_type | VARCHAR(40) | Option code; default `other` |
| address / city / state / pincode / phone / email | VARCHAR | Optional contact |
| gst_number | VARCHAR(30) NULL | GSTIN |
| fssai_number | VARCHAR(50) NULL | Optional (food-service) |
| bill_number_prefix | VARCHAR(20) NULL | e.g. `INV-2026-` |
| default_gst_percent | DECIMAL(5,2) NULL | Optional default for new items |
| status | VARCHAR(20) | `ACTIVE` \| `SUSPENDED` (deactivate = SUSPENDED) |
| created_at / updated_at | DATETIME(6) | |

### `roles`

Global seed: `OWNER`, `BILLING_USER`. Not tenant-scoped. `name` UNIQUE.

### `users`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK → tenants | Indexed |
| role_id | FK → roles | |
| name | VARCHAR(120) | |
| email | VARCHAR(255) | Unique per tenant: `(tenant_id, email)` |
| password_hash | VARCHAR(255) | Never exposed in API |
| is_active | BOOLEAN | |
| email_verified | TINYINT | |
| email_verified_at | DATETIME NULL | |
| password_changed_at | DATETIME NULL | |
| pending_email | VARCHAR(255) NULL | Profile email change |
| token_version | INT | Bumped on logout / password change |
| last_login_at | DATETIME NULL | |
| created_at / updated_at | DATETIME(6) | |

### `password_reset_tokens` / `email_verification_tokens`

Hashed `token_hash` UNIQUE; FK `user_id` **ON DELETE CASCADE**; `expires_at`, optional `used_at`.

### `categories`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | |
| parent_id | CHAR(36) NULL FK → categories | Subcategory support |
| parent_key | CHAR(36) GENERATED VIRTUAL | `IFNULL(parent_id, '')` |
| name | VARCHAR(120) | |
| description | TEXT NULL | |
| is_active | BOOLEAN | |
| created_at / updated_at | DATETIME(6) | |

**Unique:** `(tenant_id, parent_key, name)` — not `(tenant_id, parent_id, name)`.

### `items`

Catalog: `price`, `gst_percentage`, optional `sku` / `cost_price` / `stock_quantity`, `created_by` SET NULL, soft `is_active`. UNIQUE `(tenant_id, name)`; SKU unique per tenant when set.

### `bill_number_counters`

**Required** per tenant. PK = `tenant_id`; `next_value` updated in transaction.

### `bills`

Finalized sales. Column `table_number` is the API/UI **reference**. `payment_method` = `cash` \| `online`. App status default **FINALIZED**; cancel → **CANCELLED**. Optional customer name/phone/email for delivery channels. Indexes on tenant + created_at / status / payment_method.

### `bill_items`

Line snapshots (`item_name`, `unit_price`, GST amounts). `item_id` **SET NULL** on item delete. `bill_id` **RESTRICT**.

### `notifications`

Tenant in-app alerts (`type`, `title`, `message`, `entity_*`, `is_read`). Includes stock and `SUBSCRIPTION_EXPIRING` / `SUBSCRIPTION_EXPIRED`.

### `tenant_whatsapp_configs`

PK = `tenant_id`. Access token stored **encrypted**; never returned raw to clients.

### `bill_deliveries`

Attempts for `WHATSAPP` / `EMAIL` / `PRINT`. Status lifecycle includes Meta webhook updates (`DELIVERED` / `READ` / `FAILED`, etc.).

### `audit_logs`

Append-only tenant activity. Snapshots `user_name`. Entity types include BILL, ITEM, CATEGORY, USER, AUTH, REPORT, etc.

### `stock_movements`

Inventory ledger: receive / adjust; `item_id` RESTRICT; `created_by` SET NULL.

---

## Phase 8 tables

### `master_admins`

Platform operators — **no** `tenant_id`. Columns: `name`, unique `email`, `password_hash`, `is_active`, `token_version`, `last_login_at`.

### `registration_requests`

Public signup queue. Status `PENDING` / `APPROVED` / `REJECTED`. Stores `password_hash` until approve (never returned by API). Optional `approved_by` / `rejected_by` → `master_admins`; `tenant_id` set on approve.

### `platform_settings`

Singleton trial config: `trial_enabled`, `trial_days`, `expiry_warning_days`.

### `subscription_plans`

Master catalog: price, `billing_cycle` MONTHLY|YEARLY, features JSON, `trial_eligible`, `is_public`, `is_active`, `display_order`.

### `subscriptions`

Per-tenant entitlement: status TRIAL/ACTIVE/EXPIRED/CANCELLED/SUSPENDED (plus derived EXPIRING in API), `plan_id` SET NULL, `price_at_purchase` snapshot, trial/paid end dates, `payment_status` (e.g. COMPLIMENTARY / MANUAL).

### `subscription_notices`

Idempotency: UNIQUE `(subscription_id, notice_type, period_key)`.

### `platform_notifications`

Master in-app alerts (no `tenant_id`): title, message, type, entity refs, `is_read`.

### `platform_audit_logs`

Master actions only. Optional `tenant_id`, `actor_id` → `master_admins` SET NULL. Secrets stripped before write.

---

## Bill status (application)

```text
(create) ──► FINALIZED ──cancel──► CANCELLED
```

SQL CHECK may still allow DRAFT/VOID for forward compatibility; the app creates FINALIZED only.

## Money & GST

- Store amounts with 2 decimal places  
- Split GST into CGST + SGST (equal halves for intra-state model)  
- Backend recalculates; reject mismatched client totals  

## Referential integrity

See [database-relationships.md](./database-relationships.md). Soft-deactivate users/items/categories; never wipe financial history via API.

## Schema apply

| Scenario | Command |
|----------|---------|
| Fresh | `01_create_database.sql` + `02_schema.sql` |
| Existing / hosted | `apply_pending_schema.py` then `stamp_alembic_head.py` |
| Obsolete | Do **not** run `03_saas_auth_alter.sql` |
