# SQL & Schema Apply Guide

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Canonical greenfield schema:** `02_schema.sql` (23 application tables)  
**Live hosted DB (current):** `u583892242_HotelBillingDB` — **24** objects = 23 app tables + `alembic_version` stamped `20260818_phase8_saas`. Do **not** re-run `02_schema.sql` there.

---

## Application tables (23)

### Core / tenant-scoped (15)

`tenants`, `roles`, `users`, `password_reset_tokens`, `email_verification_tokens`, `categories`, `items`, `bill_number_counters`, `bills`, `bill_items`, `notifications`, `tenant_whatsapp_configs`, `bill_deliveries`, `audit_logs`, `stock_movements`

### Phase 8 SaaS / Master control plane (8)

| Table | Purpose |
|-------|---------|
| `master_admins` | Platform operators (no `tenant_id`) |
| `registration_requests` | Public signup queue |
| `platform_settings` | Trial defaults singleton |
| `subscription_plans` | Plan catalog |
| `subscriptions` | Per-tenant entitlement |
| `subscription_notices` | Expiry notice idempotency |
| `platform_notifications` | Master in-app alerts |
| `platform_audit_logs` | Master action audit |

---

## Fresh database (empty / local only)

1. `01_create_database.sql` — create DB (legacy name `hotel_billing` is OK)
2. `02_schema.sql` — full current schema (**drops** tables first — **never** on production)

Optional: `python sql/apply_schema.py` if your ops flow uses that helper.

---

## Existing / hosted database (upgrade)

Prefer **one** of the paths below. Always **inspect** first.

### 0) Inspect first (read-only, required on live)

`inspect_database_schema.py` and `apply_pending_schema.py` load `backend/.env` and accept either `DATABASE_URL` **or** split `MYSQL_HOST` / `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_DATABASE` / `MYSQL_PORT`.

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out schema-report.json
.\.venv\Scripts\python.exe scripts\check_platform_ready.py
```

Reports: table inventory, Phase 8 present/missing, `alembic_version`, key row counts (including `master_admins`).

### A) Idempotent Python helpers (operational path for live)

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\apply_pending_schema.py
.\.venv\Scripts\python.exe scripts\stamp_alembic_head.py
```

`stamp_alembic_head.py` writes `alembic_version = 20260818_phase8_saas` only. It does not drop tables.

Runs helpers in order:

1. `apply_saas_auth_schema.py`
2. `apply_item_created_by.py`
3. `apply_bill_payment_method.py`
4. `apply_tenant_business_type.py`
5. `apply_schema_relationship_fixes.py`
6. `apply_item_catalog_fields.py`
7. `apply_category_parent_key.py`
8. `apply_bill_report_index.py`
9. `apply_stock_notifications.py`
10. `apply_whatsapp_bill_delivery.py`
11. `apply_users_email_unique.py`
12. `apply_whatsapp_webhook_statuses.py`
13. `apply_email_bill_delivery.py`
14. `apply_stock_movements.py`
15. `apply_stock_receive.py`
16. `apply_perf_indexes.py`
17. `apply_master_admins.py`
18. `apply_registration_requests.py`
19. `apply_trial_management.py`
20. `apply_subscription_plans.py`
21. `apply_subscription_lifecycle.py`
22. `apply_expiry_notifications.py`
23. `apply_platform_audit.py`

Hostinger is **MariaDB**: CHECK drops use `DROP CONSTRAINT` then `DROP CHECK` via `scripts/schema_helpers.py`.

### B) Alembic

- **Empty DB that never used helpers:** `flask db upgrade` can apply the revision chain (head includes `20260818_phase8_saas`).
- **Existing hosted DB that already ran helpers:** **stamp**, do **not** `flask db upgrade` from a missing/`empty` `alembic_version`.

### Master Admin seed (after schema ready)

If `master_admins` count is **0**, set `MASTER_ADMIN_EMAIL` / `MASTER_ADMIN_PASSWORD` in `.env` (do not commit), then:

```powershell
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

Use `.\.venv\Scripts\python.exe` (not bare `scripts\seed_master_admin.py`). Sign in at `/master/login`.

---

## Obsolete file

`03_saas_auth_alter.sql` — **historical auth-only alter**. Do **not** apply it for upgrades. Use helpers or fresh `02_schema.sql`.

---

## Do not mix blindly

- Do **not** re-run `02_schema.sql` on a production DB (it drops tables).
- Use `02_schema.sql` only for empty/dev rebuilds.
- Keep `02_schema.sql` as the greenfield source of truth whenever you add or change tables, columns, constraints, or indexes.

See also: [`docs/database-design.md`](../../docs/database-design.md), [`docs/database-relationships.md`](../../docs/database-relationships.md), [`docs/backup-and-recovery.md`](../../docs/backup-and-recovery.md).
