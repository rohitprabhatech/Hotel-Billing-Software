# Database Design — Business Billing

**Canonical summary (Phase 8 + follow-on Sprints 1–15).**  
Detailed catalog: [07-database-design.md](./07-database-design.md). Relationships: [database-relationships.md](./database-relationships.md). ERD: [08-database-erd.md](./08-database-erd.md). SQL guide: [`backend/sql/README.md`](../backend/sql/README.md).

## Current project status (schema)

| Fact | Value |
|------|--------|
| Greenfield source of truth | `backend/sql/02_schema.sql` (**23** app tables) |
| Hosted DB | `u583892242_HotelBillingDB` on Hostinger (MariaDB) |
| Live object count | **24** = 23 app tables + `alembic_version` |
| Alembic head (stamped) | `20260818_phase8_saas` |
| Phase 8 tables on live | All 8 present |
| `master_admins` rows | **0** until `seed_master_admin.py` succeeds |
| Production upgrade path | Inspect → backup → `apply_pending_schema.py` → `stamp_alembic_head.py` |
| Never on live | `02_schema.sql` (drops tables), `03_saas_auth_alter.sql` |

Phase 8 product work and the cloud/Master follow-on program (Sprints 1–15) are **signed off**. Open ops: seed the first Master Admin.

## Principles

1. Shared MySQL/MariaDB schema; **tenant isolation via `tenant_id`** on every business-scoped table  
2. Money as `DECIMAL`; never float  
3. Soft deactivate for categories/items; bills **cancel** (no hard delete of financial rows)  
4. **`bill_items` store line snapshots** (name, price, GST) so history survives catalog edits  
5. Never trust client-supplied `tenant_id` for authorization  
6. Master Admin is **not** a tenant user (`master_admins`, no `tenant_id`)

## Core tables (15)

| Table | Purpose |
|-------|---------|
| `tenants` | Business workspace: `business_name`, **`business_type`**, address, GST, optional FSSAI, bill prefix, status (`ACTIVE` / `SUSPENDED`) |
| `roles` | Global: `OWNER`, `BILLING_USER` |
| `users` | Tenant-scoped accounts; `token_version` invalidates JWT after password change; email verify / pending email fields |
| `password_reset_tokens` / `email_verification_tokens` | Hashed tokens + expiry |
| `categories` | Optional `parent_id` hierarchy; generated `parent_key` for unique main names; `is_active` soft flag |
| `items` | Catalog: price, GST%, optional **SKU**, **cost_price**, **stock_quantity**; soft `is_active` |
| `bill_number_counters` | Per-tenant sequence (**required**) |
| `bills` | Finalized sales; **`payment_method`** `cash` \| `online`; reference stored in column `table_number` (API/UI: **reference**); optional customer contact for WhatsApp/email |
| `bill_items` | Line snapshots; `item_id` may become NULL if item removed from catalog |
| `bill_deliveries` | Delivery attempts (`WHATSAPP` / `EMAIL` / `PRINT`); status lifecycle includes webhook updates |
| `tenant_whatsapp_configs` | Per-tenant WhatsApp Cloud API config; access token stored **encrypted** |
| `notifications` | Tenant in-app alerts (stock, subscription expiry, delivery failures) |
| `audit_logs` | Append-only tenant activity |
| `stock_movements` | Inventory ledger (receive / adjust) |

## Phase 8 tables (8)

| Table | Purpose |
|-------|---------|
| `master_admins` | Platform operators — **no** `tenant_id` |
| `registration_requests` | Public signup queue (`PENDING` / `APPROVED` / `REJECTED`); tenant+owner created on approve |
| `platform_settings` | Singleton: `trial_enabled`, `trial_days` (default 15), `expiry_warning_days` |
| `subscription_plans` | Master-managed catalog (price, cycle, features, public/active flags) |
| `subscriptions` | Tenant trial/paid entitlement; `plan_id` FK (nullable); `price_at_purchase` snapshot; complimentary rows use `payment_status=COMPLIMENTARY` and `ends_at` NULL |
| `subscription_notices` | Idempotency log for expiry notices |
| `platform_notifications` | Master Admin in-app alerts (no `tenant_id`) |
| `platform_audit_logs` | Append-only Master actions (approve/reject, plans, trial settings, activate/deactivate/suspend). Never stores passwords or tokens |

## Business types

Stored as codes on `tenants.business_type` (examples):  
`restaurant`, `hotel`, `clothing_store`, `footwear_store`, `kirana_store`, `grocery_store`, `electronics_store`, `retail_shop`, `other`.

FSSAI is optional and primarily relevant for restaurant/hotel types.

## Schema application

| Scenario | Path |
|----------|------|
| Fresh / empty DB | `01_create_database.sql` + `02_schema.sql` (or `apply_schema.py`) |
| Existing / hosted | Inspect → `apply_pending_schema.py` → `stamp_alembic_head.py` |
| Master login ready | `check_platform_ready.py` then `seed_master_admin.py` |

Default local database name may still be `hotel_billing` (legacy); product name is **Business Billing**.

### Category root uniqueness

MySQL/MariaDB does not treat multiple `NULL` `parent_id` values as colliding under `UNIQUE (tenant_id, parent_id, name)`. Fresh and upgraded schemas use:

- `parent_key CHAR(36) GENERATED ALWAYS AS (IFNULL(parent_id, '')) VIRTUAL`
- `UNIQUE (tenant_id, parent_key, name)`

Application `find_by_tenant_parent_name` remains the first line of defense; the DB unique key closes races / direct SQL inserts.
