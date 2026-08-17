# Database Relationships

**Sprint:** 4 — Database relationship refactor  
**Canonical greenfield schema:** `backend/sql/02_schema.sql`  
**Product:** Multi-business billing SaaS (shared MySQL DB + `tenant_id`)

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

**Application rule:** Soft-deactivate items/categories; cancel bills. Do not hard-delete financial rows via API.

---

## 3. Primary keys, uniques, indexes

| Table | PK | Notable uniques | Key indexes |
|-------|----|-----------------|-------------|
| tenants | `id` | — | `status`, `business_name`, `business_type` |
| roles | `id` | `name` | — |
| users | `id` | `(tenant_id, email)` | tenant, tenant+role, tenant+active |
| categories | `id` | `(tenant_id, parent_key, name)` | tenant, tenant+active, parent |
| items | `id` | `(tenant_id, name)` | tenant, tenant+category, tenant+active, created_by |
| bills | `id` | `(tenant_id, bill_number)`, `(tenant_id, bill_sequence)` | tenant+created_at/status/created_by/payment_method; composite status+created_at |
| bill_items | `id` | — | tenant+bill, tenant+item |
| bill_deliveries | `id` | — | tenant+bill, tenant+created, **tenant+method+bill+created**, provider_message_id |
| stock_movements | `id` | — | tenant+created, tenant+item, **tenant+item+created** |
| notifications | `id` | — | tenant+created, tenant+unread, tenant+entity |
| audit_logs | `id` | — | tenant+created_at/user/action/entity |
| bill_number_counters | `tenant_id` | — | — |
| password_reset_tokens | `id` | `token_hash` | `user_id` |
| email_verification_tokens | `id` | `token_hash` | `user_id` |

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
- Isolation is enforced in repositories/services (JWT → request context → filters).
- There is **no** MySQL RLS. New queries must always scope by `tenant_id`.

---

## 6. Schema sources of truth

| Path | Use |
|------|-----|
| `backend/sql/01_create_database.sql` | Create empty DB |
| `backend/sql/02_schema.sql` | **Fresh install** — full current schema |
| `backend/sql/03_saas_auth_alter.sql` | Legacy alter notes (superseded by Alembic/helpers for upgrades) |
| `backend/migrations/versions/*` | Incremental upgrades for existing DBs |
| `backend/scripts/apply_pending_schema.py` | Run all idempotent apply helpers in order |

### Upgrade order (Alembic)

1. `20260326_saas_auth`  
2. `20260326_item_created_by`  
3. `20260326_bill_payment_method`  
4. `20260814_tenant_business_type`  
5. `20260814_schema_rel_fixes`  
6. `20260814_item_catalog_fields`  
7. `20260814_category_parent_key`  
8. `20260814_bill_report_index`  

Or: `python scripts/apply_pending_schema.py` with `DATABASE_URL` set (includes email delivery, stock ledger, and `apply_perf_indexes.py`).

### ORM load notes (speed)

- `Bill.items` uses **`lazy="selectin"`** (not `joined`) so bill **list** endpoints do not JOIN every line item.
- List queries also use `noload(Bill.items)` + `joinedload(Bill.creator)`.
- Detail/`get_by_id` still `joinedload(Bill.items)`.
- WhatsApp + email latest status for a page of bills loads in **one** delivery query.

---

## 7. Known intentional asymmetries

1. **DRAFT / VOID** remain in CHECK for forward compatibility; app currently creates **FINALIZED** only.  
2. **Email uniqueness** is per-tenant in DB; registration service currently blocks globally — product policy (Sprint 21 may revisit).  
3. **Inactive item names** still occupy `uq_items_tenant_name` — reactivation/rename required to reuse a name.  
4. DB name `hotel_billing` is legacy; product branding is multi-business.  
5. **Category root uniqueness:** MySQL treats `NULL` as distinct in multi-column UNIQUE keys. Schema uses generated `parent_key` so two main categories cannot share a name in the same tenant.

---

## 8. Verification checklist (Phase 2 / P2-5)

- [x] PKs/FKs/`tenant_id` reviewed  
- [x] Cascade policy documented  
- [x] `02_schema.sql` aligned with ORM (`parent_key`, bill default, bill_items SET NULL, business_type)  
- [x] Alembic + `apply_category_parent_key.py` for root uniqueness  
- [x] `update_item` rejects inactive category (matches create)  
- [x] Single pending-upgrade entry point documented  
