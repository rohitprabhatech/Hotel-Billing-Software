# Database Design — Business Billing

**Canonical summary (Sprint 19).** Detailed column catalog: [07-database-design.md](./07-database-design.md). Relationships: [database-relationships.md](./database-relationships.md).

## Principles

1. Shared MySQL schema; **tenant isolation via `tenant_id`** on every business-scoped table  
2. Money as `DECIMAL`; never float  
3. Soft deactivate for categories/items; bills **cancel** (no hard delete of financial rows)  
4. **`bill_items` store line snapshots** (name, price, GST) so history survives catalog edits  
5. Never trust client-supplied `tenant_id` for authorization  

## Core tables

| Table | Purpose |
|-------|---------|
| `tenants` | Business workspace: `business_name`, **`business_type`**, address, GST, optional FSSAI, bill prefix, status |
| `roles` | Global: `OWNER`, `BILLING_USER` |
| `users` | Tenant-scoped accounts; `token_version` invalidates JWT after password change |
| `categories` | Optional `parent_id` hierarchy; generated `parent_key` for unique main names; `is_active` soft flag |
| `items` | Catalog: price, GST%, optional **SKU**, **cost_price**, **stock_quantity**; soft `is_active` |
| `bills` | Finalized sales; **`payment_method`** `cash` \| `online`; reference stored in column `table_number` (API/UI: **reference**); optional customer name/phone (E.164) for WhatsApp |
| `bill_deliveries` | Delivery attempts (`WHATSAPP`); status `PENDING`/`SENT`/`FAILED`; tenant-scoped; separate from bill financial status |
| `tenant_whatsapp_configs` | Per-tenant WhatsApp Cloud API config; access token stored **encrypted**; never returned to clients |
| `bill_items` | Line snapshots; `item_id` may become NULL if item removed from catalog |
| `bill_number_counters` | Per-tenant sequence |
| `audit_logs` | Append-only activity |
| `password_reset_tokens` / `email_verification_tokens` | Hashed tokens + expiry |

## Business types

Stored as codes on `tenants.business_type` (examples):  
`restaurant`, `hotel`, `clothing_store`, `footwear_store`, `kirana_store`, `grocery_store`, `electronics_store`, `retail_shop`, `other`.

FSSAI is optional and primarily relevant for restaurant/hotel types.

## Schema application

- Fresh DB: `backend/sql/01_create_database.sql` + `02_schema.sql` (or `apply_schema.py`)  
- Existing DB: Flask-Migrate / `flask db upgrade` and/or `backend/scripts/apply_pending_schema.py` (includes `apply_category_parent_key.py`)  

Default local database name may still be `hotel_billing` (legacy); product name is **Business Billing**.

### Category root uniqueness (P2-5)

MySQL does not treat multiple `NULL` `parent_id` values as colliding under `UNIQUE (tenant_id, parent_id, name)`. Fresh and upgraded schemas use:

- `parent_key CHAR(36) GENERATED ALWAYS AS (IFNULL(parent_id, '')) VIRTUAL`
- `UNIQUE (tenant_id, parent_key, name)`

Application `find_by_tenant_parent_name` remains the first line of defense; the DB unique key closes races / direct SQL inserts. VIRTUAL (not STORED) avoids MySQL ALTER rebuild failures (errno 1215) on existing self-FK tables.
