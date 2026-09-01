# Database Audit Report

**Date:** 2026-09-01  
**Scope:** Full backend inspection — models, migrations, services, repositories, tests  
**Approach:** Inspect → document → safe fixes only (no destructive schema rewrites)

---

## Executive summary

The database architecture is **fundamentally sound** for a multi-business billing SaaS: **shared schema**, **row-level tenant isolation**, **UUID primary keys**, **shared core billing/inventory tables**, and **industry extensions** via additional tables + module gating — **not** per-business duplicate tables.

**Production readiness:** **Conditionally ready** — core design passes isolation and financial flow review; address documented medium risks (doc drift, public image URLs, business-type data mixing on type switch) before high-traffic cloud launch.

---

## 1. Current database architecture

| Aspect | Finding |
|--------|---------|
| Pattern | Shared database, shared schema, multi-tenant row isolation |
| Business entity | `tenants` table (1 tenant = 1 business) |
| Tenant key | `tenant_id` FK on ~85 operational tables |
| Business type | `tenants.business_type` — module configuration, not data partition |
| PK strategy | UUID `String(36)`; counters use `tenant_id` as PK |
| ORM | SQLAlchemy 2.x via Flask |
| Migrations | Alembic / Flask-Migrate, 60 revisions |
| Greenfield DDL | `backend/sql/02_schema.sql` (96 tables) |
| Copy for ops | `database/schema.sql` |

---

## 2. Actual business types (13 canonical)

From `backend/app/constants/business_types.py`:

1. `hotel_restaurant` — Hotels / Restaurants  
2. `cafe_tea` — Cafes / Tea Shops  
3. `grocery_kirana` — Grocery / Kirana  
4. `clothing` — Clothing Shops  
5. `mobile` — Mobile Shops  
6. `hardware` — Hardware / Building Material (legacy `building_material` → `hardware`)  
7. `bakery_sweet` — Bakery / Sweet Shops  
8. `stationery` — Stationery Shops  
9. `electronics` — Electronics Shops  
10. `furniture` — Furniture Shops  
11. `book_store` — Book Stores  
12. `wholesale` — Wholesale Shops  
13. `travel_agency` — Travel Agencies  

**No `business_id` column** on operational tables. See [04-business-type-models.md](./04-business-type-models.md).

---

## 3. Total tables: 96

| Category | Count (approx) |
|----------|----------------|
| Platform / SaaS | 10 |
| Tenant core | 6 |
| Shared billing/commerce | 25 |
| Inventory/catalog | 15 |
| Restaurant/cafe | 12 |
| Mobile/electronics/service | 8 |
| Wholesale/trade docs | 14 |
| Travel | 8 |
| Counters (PK=tenant_id) | 16 |

Full index: [05-table-reference.md](./05-table-reference.md)

---

## 4. Shared vs business-specific models

### A. Global / platform
`master_admins`, `roles`, `subscription_plans`, `platform_settings`, `platform_notifications`, `platform_audit_logs`, `registration_requests`

### B. Shared billing (all tenants)
`tenants`, `users`, `customers`, `suppliers`, `categories`, `items`, `bills`, `bill_items`, `purchases`, `expenses`, `stock_movements`, `audit_logs`, …

### C. Industry extensions (module-gated)
Restaurant: `dining_tables`, `orders`, `kots`  
Cafe: `item_addons`, `combos`, `coupons`  
Clothing: `item_variants`, `item_images`, `sales_returns`  
Mobile/Electronics: `serial_units`, `repair_orders`  
Hardware/Wholesale: `quotations`, `warehouses`, `sales_orders`  
Bakery: `production_runs`, `custom_product_orders`  
Travel: `travel_bookings`, `tour_packages`, `travel_agents`  

**No duplicate `hotel_customers` / `grocery_items` tables.**

---

## 5. Duplicate models audit

**Result: PASS** — no unnecessary per-business duplicate master tables.

Parallel document families (`orders` vs `sales_orders` vs `purchase_orders`) are **intentional** distinct workflows.

---

## 6. Tenant architecture

**Decision:** Direct `tenant_id` on tenant-owned rows (not derived through `business_id`).

**Enforcement chain:**
JWT → `RequestContext` → `require_request_context()` → repository filters

**Not used:** PostgreSQL RLS, SQLAlchemy global filter, separate DB per tenant

**Tests:** 40+ files + `test_biz64_tenant_isolation_regression_suite.py` (@pytest.mark.isolation)

**Status: PASS** (with noted image URL exception)

---

## 7. Business isolation

**Important clarification:** Business type does **not** isolate data within a tenant.

When owner changes `business_type` in Settings:
- Module APIs change (KOT hidden for grocery, etc.)
- **Existing items, bills, orders remain** in same tables

This is **configuration isolation**, not **data silo per business type**.

**Recommendation (medium):** Document in UI that switching type does not archive prior industry data. Optional future: `tenant_module_data` flags — **not implemented**.

**Status: PASS** for SaaS tenant isolation; **INFORM** for business-type data mixing on switch

---

## 8. Primary key design

| Pattern | Usage |
|---------|--------|
| UUID string PK | All entities |
| tenant_id as PK | Number counters, WhatsApp config |

**Decision:** Keep UUIDs — do not migrate to integer PKs in production.

**Status: PASS** (consistent)

---

## 9. Foreign keys & relationships

- Core FKs use `ON DELETE RESTRICT` on tenant relationships
- `bill_items.item_id` → SET NULL on item delete (preserves history)
- Deferred FK for `bill_items.serial_unit_id` in greenfield SQL (cycle break)

**Issues found:**
- Some migrations use `except Exception: pass` — CHECK constraints may silently fail on drifted DBs

**Status: PASS** with migration hygiene notes

---

## 10. Delete / cascade strategy

| Model | Strategy |
|-------|----------|
| Customer, Item, Category, User | `is_active = false` |
| Bill | Cancel (`status=CANCELLED`), not delete |
| BillItem | Retained; historical |
| AuditLog | `is_deleted` flag (owner cleanup) |
| Purchase | Cancel + stock reversal where implemented |

**Status: PASS** — financial history preserved

---

## 11. Financial data protection

- Totals calculated in `BillService` before insert
- GST/discount/service charge/transport handled in service layer
- Credit bills update `customers.balance` + ledger

**Validation:** pytest billing suites; manual integrity script added

**Status: PASS**

---

## 12. Invoice numbering

- `BillNumberCounter` per tenant
- `allocate_bill_number()` uses **`with_for_update()`** row lock
- Sequence stored in DB — not frontend-generated

**Status: PASS**

---

## 13. Inventory design

**Single strategy:** `items.stock_quantity` + `stock_movements` audit

**Deduction timing:**
- POS bill create → immediate
- Restaurant → on order settlement → bill

**Warehouse:** Additional `warehouse_stocks` when module enabled

**Recipe:** `RecipeStockService` on bill finalize for menu items

**Risks:** Dual stock (`items.stock_quantity` + `warehouse_stocks`) requires careful warehouse-aware billing — implemented for warehouse module paths

**Status: PASS** with warehouse complexity noted

---

## 14–17. Industry-specific audits

See [04-business-type-models.md](./04-business-type-models.md) and per-business `docs/05-businesses/*/database.md`.

Hotel/Cafe flow verified in models: `dining_tables` → `orders` → `kots` → `bills`

---

## 18. Index audit

Performance migration: `20260826_biz66_perf_indexes`  
Bill report index script: `apply_bill_report_index.py`

Common indexed columns: `tenant_id`, `created_at`, `status`, FK columns

**Recommendation:** Run `EXPLAIN` on dashboard/report queries in production with realistic volume

**Status: PASS** (baseline indexes present)

---

## 19. Unique constraints

- SKU/barcode uniqueness scoped per tenant (application + tests)
- `users.email` — **global unique** (platform-wide, not per tenant)
- Bill numbers — unique per tenant via counter + sequence

**Status: PASS** (note global email constraint)

---

## 20. SQL query optimization

- Reports use SQL `SUM`/`COUNT` aggregations (`ReportRepository`, `BillRepository.today_sales_total`)
- List endpoints use pagination (`page`, `per_page`)
- Bill list uses `joinedload` for items/creator

**Potential N+1:** Review new list endpoints as added — no systemic N+1 found in core billing

**Status: PASS** (ongoing vigilance)

---

## 21–22. Dashboard & pagination

Dashboard KPIs query aggregated SQL — not full table scans in Python.

Pagination: bills, customers, items, audit logs, stock movements — **implemented**.

**Status: PASS**

---

## 23. Transactions

Bill creation wraps stock, bill rows, counter, audit in single SQLAlchemy session commit.

**Status: PASS**

---

## 24. Concurrency

- Bill numbers: `FOR UPDATE` on counter ✓
- Stock: item row lock in repository ✓

**Status: PASS**

---

## 25. Migration audit

| Issue | Severity |
|-------|----------|
| 60 migrations, linear chain | OK |
| Docs cite old head (`20260827_cafe_coupons`) | Medium — **updated in this audit** |
| Alembic assumes 10 core tables from bootstrap SQL | By design |
| Silent `except: pass` in some migrations | Medium |
| `02_schema.sql` destructive DROP ALL | Expected for greenfield only |

**Status: PASS** with documentation fixes

---

## 26–27. SQL schema & cloud readiness

- `database/schema.sql` — copy of canonical DDL
- `DATABASE_URL` from environment — no secrets in source
- Connection pool configured in `settings.py`:
  - `pool_size=5`, `max_overflow=10`, `pool_recycle=280`, `pool_pre_ping=True`
- Production config validates strong secrets

See [17-cloud-database-deployment.md](./17-cloud-database-deployment.md)

**Status: READY** (configurable via env)

---

## 28–29. Connection pool & security

Production tuning via:
`DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_TIMEOUT`

SQL injection: SQLAlchemy parameterized queries throughout

**Gap:** `GET /item-images/files/<uuid>` — **unauthenticated** if filename known (UUID obscurity)

**Status: PASS** with one medium security note

---

## 30. Backup & recovery

Documented in [18-backup-and-recovery.md](./18-backup-and-recovery.md) — operator responsibility on cloud provider

**Status: DOCUMENTED**

---

## 31. Data validation

Script added: `backend/scripts/validate_database_integrity.py` (report-only)

**Status: READY**

---

## 32–33. ERD diagrams

Created in `docs/03-database/erd/` — Mermaid format

**Status: COMPLETE** (core diagrams; extend as needed)

---

## 38. API ↔ database mapping (summary)

| API | Service | Tables |
|-----|---------|--------|
| POST `/bills` | `BillService.create_bill` | bills, bill_items, stock_movements, bill_number_counters, customers, serial_units, audit_logs |
| POST `/purchases` | `PurchaseService` | purchases, purchase_items, stock_movements, items |
| POST `/orders` | `OrderService` | orders, order_items, kots |
| GET `/reports/*` | `ReportService` | bills, items, aggregates |
| GET `/audit-logs` | `AuditLogService` | audit_logs |

---

## 39. Database test suite

| Suite | Purpose |
|-------|---------|
| `test_tenant_isolation.py` | Baseline |
| `test_p2_13_tenant_isolation_matrix.py` | Cross-tenant matrix |
| `test_biz64_tenant_isolation_regression_suite.py` | Industry IDOR |
| `test_billing.py`, `test_biz06_purchases.py`, etc. | Domain flows |
| `test_schema_relationships.py` | FK/business_type column |

Run: `pytest -m isolation` and full backend suite before production deploy

**Status: PASS** (extensive coverage)

---

## Problems fixed in this audit

| Fix | File |
|-----|------|
| Updated database overview (was "23 tables") | `docs/03-database/01-database-overview.md` |
| Business type → models mapping | `docs/03-database/04-business-type-models.md` |
| Team guide | `docs/03-database/20-team-database-guide.md` |
| ERD diagrams | `docs/03-database/erd/*.md` |
| Integrity validation script | `backend/scripts/validate_database_integrity.py` |
| Production schema copy + README | `database/schema.sql`, `database/README.md` |
| Cloud & backup docs | `17-cloud-database-deployment.md`, `18-backup-and-recovery.md` |
| Production checklist | `40-production-readiness-checklist.md` |
| Table reference index | `05-table-reference.md` |

---

## Changes intentionally NOT made

- No new tables created
- No PK type changes
- No dropped migrations
- No `business_id` column added (tenant_id architecture kept)
- No PostgreSQL RLS added
- No rewrite of 96-table schema

---

## Remaining risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Business type switch leaves old industry data visible | Medium | UI warning; optional archive feature later |
| Public item image file URL | Medium | Add auth or signed URLs |
| Migration silent failures | Medium | Run `flask db upgrade` on staging; verify CHECK constraints |
| Global unique user email | Low | Document; consider per-tenant email in future |
| Doc drift in older sprint docs | Low | Point to `03-database/` as canonical |
| `02_schema.sql` vs migration CHECK drift | Low | Prefer migrations on hosted DB |

---

## Final production readiness status

| Area | Status |
|------|--------|
| Architecture | **Sound** |
| Tenant isolation | **Pass** |
| Financial integrity | **Pass** |
| Inventory model | **Pass** |
| Migrations | **Pass** (with ops discipline) |
| Cloud config | **Ready** |
| Documentation | **Complete** (this audit pass) |
| ERD | **Complete** (core set) |

**Overall: CONDITIONALLY PRODUCTION READY** — deploy after staging migration test, backup policy, and integrity script run on production clone.
