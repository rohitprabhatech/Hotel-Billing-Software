# Database Relationships

**Phase 8 + follow-on (Sprints 1–15)**  
**Canonical greenfield schema:** `backend/sql/02_schema.sql` (23 application tables)  
**Product:** Multi-business billing SaaS (shared MySQL/MariaDB + `tenant_id`)

---

## 1. Entity relationship map

```
roles (global)
   ▲
   │ role_id
users ──────────────► tenants
   │                    ▲
   │                    │ tenant_id (RESTRICT)
   ├─ password_reset_tokens (CASCADE on user delete)
   ├─ email_verification_tokens (CASCADE on user delete)
   │
tenants
   ├── categories (parent_id → categories, RESTRICT)
   │      └── items (created_by → users SET NULL)
   ├── bill_number_counters (PK = tenant_id)
   ├── bills (created_by / cancelled_by → users RESTRICT)
   │      ├── bill_items (item_id → items SET NULL; snapshots keep name/price/GST)
   │      └── bill_deliveries (WHATSAPP / EMAIL / PRINT attempts)
   ├── tenant_whatsapp_configs (PK = tenant_id)
   ├── notifications
   ├── stock_movements (item_id → items RESTRICT; inventory ledger)
   └── audit_logs (user_id → users RESTRICT, nullable)

master_admins (platform — no tenant_id)
platform_settings (singleton trial config)
registration_requests ──► master_admins (approved_by / rejected_by SET NULL)
                       └──► tenants (tenant_id SET NULL, set on approve)
subscription_plans (platform catalog)
subscriptions ──► tenants (tenant_id RESTRICT)
               └──► subscription_plans (plan_id SET NULL)
subscription_notices ──► subscriptions (subscription_id RESTRICT)
                      └──► tenants (tenant_id RESTRICT)
platform_notifications (Master Admin — no tenant_id)
platform_audit_logs ──► master_admins (actor_id SET NULL)
                     └──► tenants (tenant_id SET NULL, optional)
```

---

## 2. Cascade / delete policy

| Relationship | ON DELETE | Why |
|--------------|-----------|-----|
| `*.tenant_id → tenants` | **RESTRICT** | Never wipe a business by deleting tenant while data exists |
| `users.role_id → roles` | **RESTRICT** | Roles are global seeds |
| `categories.parent_id → categories` | **RESTRICT** | Block deleting parent while children exist (app also enforces) |
| `items.category_id → categories` | **RESTRICT** | Catalog integrity |
| `items.created_by → users` | **SET NULL** | Keep item if creator user removed |
| `bills.created_by / cancelled_by → users` | **RESTRICT** | Financial attribution must remain |
| `bill_items.bill_id → bills` | **RESTRICT** | Soft-cancel only; no hard-delete of bills |
| `bill_items.item_id → items` | **SET NULL** | Historical line keeps name/price/GST even if catalog row disappears |
| `bill_deliveries.bill_id → bills` | **RESTRICT** | Delivery history stays with the bill |
| `bill_deliveries.attempted_by → users` | **SET NULL** | Keep attempt if user removed |
| `stock_movements.item_id → items` | **RESTRICT** | Ledger requires catalog row |
| `stock_movements.created_by → users` | **SET NULL** | Keep movement if user removed |
| Auth token tables → users | **CASCADE** | Tokens are ephemeral |
| `registration_requests.approved_by / rejected_by → master_admins` | **SET NULL** | Keep request history if Master row removed |
| `registration_requests.tenant_id → tenants` | **SET NULL** | Set on approve; optional link |
| `subscriptions.plan_id → subscription_plans` | **SET NULL** | Keep entitlement if a plan row is removed; billed price stays on the subscription |
| `subscription_notices.subscription_id → subscriptions` | **RESTRICT** | Idempotency log must stay with subscription |
| `subscription_notices.tenant_id → tenants` | **RESTRICT** | Consistent with other tenant-scoped tables |
| `platform_audit_logs.actor_id → master_admins` | **SET NULL** | Keep the action if a Master Admin row is later removed |
| `platform_audit_logs.tenant_id → tenants` | **SET NULL** | Optional link; platform audit is not tenant-scoped |

**Application rule:** Soft-deactivate items/categories; cancel bills. Do not hard-delete financial rows via API. Master **deactivate** sets `tenants.status=SUSPENDED` — data is retained.

---

## 3. Primary keys, uniques, indexes

| Table | PK | Notable uniques | Key indexes |
|-------|----|-----------------|-------------|
| tenants | `id` | — | `status`, `business_name`, `business_type` |
| roles | `id` | `name` | — |
| users | `id` | `(tenant_id, email)` | tenant, tenant+role, tenant+active |
| categories | `id` | `(tenant_id, parent_key, name)` | tenant, tenant+active, parent |
| items | `id` | `(tenant_id, name)`; SKU when set | tenant, tenant+category, tenant+active, created_by |
| bills | `id` | `(tenant_id, bill_number)`, `(tenant_id, bill_sequence)` | tenant+created_at/status/created_by/payment_method; composite status+created_at |
| bill_items | `id` | — | tenant+bill, tenant+item |
| bill_deliveries | `id` | — | tenant+bill, tenant+created, **tenant+method+bill+created**, provider_message_id |
| stock_movements | `id` | — | tenant+created, tenant+item, **tenant+item+created** |
| notifications | `id` | — | tenant+created, tenant+unread, tenant+entity |
| audit_logs | `id` | — | tenant+created_at/user/action/entity |
| bill_number_counters | `tenant_id` | — | — |
| password_reset_tokens | `id` | `token_hash` | `user_id` |
| email_verification_tokens | `id` | `token_hash` | `user_id` |
| master_admins | `id` | `email` | `is_active` |
| registration_requests | `id` | — | status, owner_email, requested_at |
| platform_settings | `id` | singleton row | — |
| subscription_plans | `id` | — | `is_active`+`is_public`+`display_order` |
| subscriptions | `id` | — | tenant, status, trial_ends, plan_id |
| subscription_notices | `id` | `(subscription_id, notice_type, period_key)` | subscription_id, tenant_id |
| platform_notifications | `id` | — | created_at, is_read |
| platform_audit_logs | `id` | — | actor_id, action, tenant_id, created_at |

---

## 4. Nullable / required notes

| Field | Nullable | Notes |
|-------|----------|-------|
| `tenants.business_type` | NO (default `other`) | Controlled option codes |
| `tenants.fssai_number` | YES | Optional; UI highlights for hotel/restaurant |
| `categories.parent_id` | YES | NULL = root / main category |
| `categories.parent_key` | NO (generated) | `IFNULL(parent_id, '')` — enforces unique main-category names per tenant |
| `items.created_by` | YES | Set on create when actor known |
| `bills.customer_email` | YES | Optional; used for email bill delivery |
| `bills.table_number` | YES | Optional counter/table/reference (hotel legacy name) |
| `bills.status` | NO (default **FINALIZED**) | SQL allows DRAFT/VOID; app uses FINALIZED/CANCELLED |
| `bill_items.item_id` | YES | Snapshot is source of truth for money/name |

---

## 5. Tenant isolation

- Every business table (except global `roles`) carries `tenant_id` **or** reaches tenant via `user_id`.
- Platform tables (`master_admins`, `platform_settings`, `subscription_plans`, `platform_notifications`, `platform_audit_logs`) have **no** tenant scope (or optional `tenant_id` on audit only).
- Isolation is enforced in repositories/services (JWT → request context → filters).
- There is **no** MySQL RLS. New queries must always scope by `tenant_id`.

---

## 6. Schema sources of truth

| Path | Use |
|------|-----|
| `backend/sql/01_create_database.sql` | Create empty DB |
| `backend/sql/02_schema.sql` | **Fresh install** — full current schema (23 tables; **DROP**s first) |
| `backend/sql/03_saas_auth_alter.sql` | **Obsolete** — do not apply |
| `backend/migrations/versions/*` | Incremental upgrades; head `20260818_phase8_saas` |
| `backend/scripts/apply_pending_schema.py` | Idempotent helpers for existing DBs |
| `backend/scripts/stamp_alembic_head.py` | Stamp live DB after helpers (do not blind-upgrade) |
| `backend/scripts/inspect_database_schema.py` | Read-only live inspect |
| `backend/scripts/check_platform_ready.py` | Schema + Master seed readiness |

### Upgrade order (Alembic chain)

1. `20260326_saas_auth`  
2. `20260326_item_created_by`  
3. `20260326_bill_payment_method`  
4. `20260814_tenant_business_type`  
5. `20260814_schema_rel_fixes`  
6. `20260814_item_catalog_fields`  
7. `20260814_category_parent_key`  
8. `20260814_bill_report_index`  
9. `20260814_stock_notifications`  
10. `20260814_whatsapp_bill_delivery`  
11. `20260814_users_email_unique`  
12. `20260814_whatsapp_webhook_statuses`  
13. `20260818_phase8_saas` (Master + subscriptions + platform audit/notifications)

**Live Hostinger path:** `apply_pending_schema.py` (includes email/stock/perf + Phase 8 helpers) → `stamp_alembic_head.py`. Do **not** `flask db upgrade` from an empty `alembic_version` on production.

### ORM load notes (speed)

- `Bill.items` uses **`lazy="selectin"`** (not `joined`) so bill **list** endpoints do not JOIN every line item.
- List queries also use `noload(Bill.items)` + `joinedload(Bill.creator)`.
- Detail/`get_by_id` still `joinedload(Bill.items)`.
- WhatsApp + email latest status for a page of bills loads in **one** delivery query.
- Master business lists: SQL pagination; status filter uses ID scan + page hydrate (Sprints 7 / 13).

---

## 7. Known intentional asymmetries

1. **DRAFT / VOID** remain in CHECK for forward compatibility; app currently creates **FINALIZED** only.  
2. **Email uniqueness** is per-tenant in DB; registration service currently blocks globally.  
3. **Inactive item names** still occupy `uq_items_tenant_name` — reactivation/rename required to reuse a name.  
4. DB name `hotel_billing` / hosted `…HotelBillingDB` is legacy naming; product branding is multi-business.  
5. **Category root uniqueness:** MySQL treats `NULL` as distinct in multi-column UNIQUE keys. Schema uses generated `parent_key`.  
6. **Account vs subscription suspend:** `tenants.status=SUSPENDED` blocks login; `subscriptions.status=SUSPENDED` allows login but locks billing (402).

---

## 8. Verification checklist

- [x] PKs/FKs/`tenant_id` reviewed  
- [x] Cascade policy documented (including Phase 8)  
- [x] `02_schema.sql` aligned with ORM (`parent_key`, bill default, bill_items SET NULL, business_type, Phase 8)  
- [x] Alembic head `20260818_phase8_saas` + live stamp path documented  
- [x] Single pending-upgrade entry point: `apply_pending_schema.py`  
- [x] Hosted DB: Phase 8 present; Master seed still open ops step  
