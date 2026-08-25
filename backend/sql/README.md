# SQL & Schema Apply Guide

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Canonical greenfield schema:** `02_schema.sql` (**53** application tables; aligned with SQLAlchemy models)  
**Upgrade path (existing / hosted DBs):** Alembic (`flask db upgrade`) — **do not** re-run `02_schema.sql` on live data.

**Alembic head (current):** `20260825_audit_db_hardening`  
(after `20260825_biz29_serial_units`)

---

## Application tables (53)

### Core / SaaS foundation

`tenants`, `roles`, `users`, `password_reset_tokens`, `email_verification_tokens`, `categories`, `items`, `bill_number_counters`, `bills`, `bill_items`, `notifications`, `tenant_whatsapp_configs`, `bill_deliveries`, `audit_logs`, `stock_movements`

### Phase 8 SaaS / Master control plane

`master_admins`, `registration_requests`, `platform_settings`, `subscription_plans`, `subscriptions`, `subscription_notices`, `platform_notifications`, `platform_audit_logs`

### BIZ industry / shared modules

| Area | Tables |
|------|--------|
| CRM / procurement | `customers`, `suppliers`, `purchases`, `purchase_items`, `purchase_number_counters`, `expenses`, `party_ledger_entries` |
| Grocery | `item_price_tiers`, `item_batches` |
| Clothing | `item_variants`, `item_images`, `sales_returns`, `sales_return_items`, `sales_return_counters` |
| F&B | `dining_tables`, `orders`, `order_items`, `order_item_addons`, `order_number_counters`, `kots`, `kot_items`, `kot_number_counters`, `recipes`, `recipe_ingredients`, `item_addon_groups`, `item_addons`, `combos`, `combo_items`, `wastage_entries` |
| Mobile / Electronics (BIZ-29) | `serial_units` (+ `items.tracks_serial`, `bill_items.serial_*`) |

---

## Fresh database (empty / local only)

1. `01_create_database.sql` — create DB (legacy name `hotel_billing` is OK)
2. `02_schema.sql` — full current schema (**drops** tables first — **never** on production)

Optional: `python sql/apply_schema.py` if your ops flow uses that helper.

Then stamp or upgrade Alembic so `alembic_version` matches head.

---

## Existing / hosted database (upgrade)

Prefer **one** of the paths below. Always **inspect** first. **Do not modify production from this agent run without an explicit ops request.**

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
- Pool: `DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`
- Financial columns: `DECIMAL` / `Numeric`
- Timezone reports: `REPORT_TIMEZONE` (default `Asia/Kolkata`)
- Migrations: linear Alembic chain; non-destructive upgrades preferred

---

## Obsolete file

`03_saas_auth_alter.sql` — **historical auth-only alter**. Do **not** apply it for upgrades.

---

## Do not mix blindly

- Do **not** re-run `02_schema.sql` on a production DB (it drops tables).
- Use `02_schema.sql` only for empty/dev rebuilds.
- Keep `02_schema.sql` aligned with models whenever tables/columns/indexes change.

See also: [`docs/backup-and-recovery.md`](../../docs/backup-and-recovery.md).
