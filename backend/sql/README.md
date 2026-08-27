# SQL & Schema Apply Guide

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Canonical greenfield schema:** `02_schema.sql` (**96** application tables; aligned with SQLAlchemy models)  
**Upgrade path (existing / hosted DBs):** Alembic (`flask db upgrade`) — **do not** re-run `02_schema.sql` on live data.

**Alembic head (current):** `20260827_cafe_coupons`  
(includes hotel billing settings audit, stock movement sources, cafe coupons; see `docs/03-database/11-alembic-revision-order.md`)

**Regenerate greenfield SQL (local only):**  
`python scripts/regenerate_02_schema.py` — overwrites `02_schema.sql` from models. Never apply the output to production.

---

## Application tables (96)

### Core / SaaS foundation

`tenants`, `roles`, `users`, `password_reset_tokens`, `email_verification_tokens`, `categories`, `items`, `bill_number_counters`, `bills`, `bill_items`, `notifications`, `tenant_whatsapp_configs`, `bill_deliveries`, `audit_logs`, `stock_movements`, `coupons`, `coupon_redemptions`

### Phase 8 SaaS / Master control plane

`master_admins`, `registration_requests`, `platform_settings`, `subscription_plans`, `subscriptions`, `subscription_notices`, `platform_notifications`, `platform_audit_logs`

### BIZ industry / shared modules

| Area | Tables |
|------|--------|
| CRM / procurement | `customers`, `suppliers`, `purchases`, `purchase_items`, `purchase_number_counters`, `expenses`, `party_ledger_entries` |
| Grocery | `item_price_tiers`, `item_batches` |
| Clothing | `item_variants`, `item_images`, `sales_returns`, `sales_return_items`, `sales_return_counters` |
| F&B | `dining_tables`, `orders`, `order_items`, `order_item_addons`, `order_number_counters`, `kots`, `kot_items`, `kot_number_counters`, `recipes`, `recipe_ingredients`, `item_addon_groups`, `item_addons`, `combos`, `combo_items`, `wastage_entries`, `coupons`, `coupon_redemptions` |
| Mobile / Electronics | `serial_units`, `repair_orders`, `repair_number_counters`, `installation_orders`, `installation_number_counters`, `item_accessories` |
| Hardware / warehouse | `warehouses`, `warehouse_stocks`, `stock_transfers`, `stock_transfer_items`, `stock_transfer_number_counters` |
| Bakery | `production_runs`, `production_run_items`, `production_run_number_counters`, `custom_product_orders`, `custom_order_payments`, `custom_order_number_counters` |
| Trade docs | `quotations`, `quotation_items`, `quotation_number_counters`, `delivery_challans`, `delivery_challan_items`, `delivery_challan_number_counters`, `sales_orders`, `sales_order_items`, `sales_order_number_counters`, `purchase_orders`, `purchase_order_items`, `purchase_order_number_counters` |
| Furniture / delivery | `delivery_jobs`, `delivery_number_counters` |
| Wholesale | `price_lists`, `price_list_items`, `customer_price_lists` |
| Travel | `tour_packages`, `travel_agents`, `travel_bookings`, `travel_booking_payments`, `travel_booking_documents`, `travel_itinerary_items`, `travel_commission_entries`, `travel_booking_number_counters` |

---

## Fresh database (empty / local only)

1. `01_create_database.sql` — create DB (legacy name `hotel_billing` is OK)
2. `02_schema.sql` — full current schema (**drops** tables first — **never** on production)

Optional: `python sql/apply_schema.py` if your ops flow uses that helper.

Then stamp Alembic so `alembic_version` matches head (`20260827_cafe_coupons`), or run `flask db upgrade` on an empty DB that already has `alembic_version` seeded.

---

## Existing / hosted database (upgrade)

Prefer **one** of the paths below. Always **inspect** first. **Do not modify production from agent runs without an explicit ops request.**

### 0) Inspect first (read-only, required on live)

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out schema-report.json
.\.venv\Scripts\python.exe scripts\check_platform_ready.py
```

### A) Alembic (preferred when chain is already stamped)

```powershell
cd backend
.\.venv\Scripts\python.exe -m flask db upgrade
```

### B) Idempotent Python helpers (legacy hosted path through Phase 8)

`scripts\apply_pending_schema.py` covers early SaaS helpers. Industry tables (BIZ-04+) are applied via **Alembic** after Phase 8 stamp.

Hostinger is **MariaDB**: CHECK drops use `DROP CONSTRAINT` then `DROP CHECK` via `scripts/schema_helpers.py`.

### Master Admin seed (after schema ready)

If `master_admins` count is **0**, set `MASTER_ADMIN_*` in `.env` (do not commit), then:

```powershell
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

---

## Cloud MySQL readiness (config only — no cloud upload)

- Charset: `utf8mb4` (URL `charset=utf8mb4` + SQLAlchemy `connect_args`)
- Collation: `utf8mb4_unicode_ci` on greenfield tables
- Pool: `DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`
- Financial columns: `DECIMAL` / `Numeric`
- Stock guard: `chk_items_stock` (`stock_quantity IS NULL OR stock_quantity >= 0`)
- Timezone reports: `REPORT_TIMEZONE` (default `Asia/Kolkata`)
- Migrations: linear Alembic chain; non-destructive upgrades preferred
- Deferred FK: `bill_items.serial_unit_id` → `serial_units` (cycle-safe `use_alter`)

---

## Obsolete file

`03_saas_auth_alter.sql` — **historical auth-only alter**. Do **not** apply it for upgrades.

---

## Do not mix blindly

- Do **not** re-run `02_schema.sql` on a production DB (it drops tables).
- Use `02_schema.sql` only for empty/dev rebuilds.
- Keep `02_schema.sql` aligned with models whenever tables/columns/indexes change (`scripts/regenerate_02_schema.py`).

See also: [`docs/03-database/10-industry-modules-ops-runbook.md`](../../docs/03-database/10-industry-modules-ops-runbook.md).
