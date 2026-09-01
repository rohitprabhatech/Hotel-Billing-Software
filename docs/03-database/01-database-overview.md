# Database Overview

**Status (audit 2026-09-01):** Production-capable shared-schema multi-tenant design with **96 application tables**, **13 canonical business types**, and **60 Alembic revisions**.

## Quick facts

| Metric | Value |
|--------|-------|
| ORM model classes | ~95 |
| Application tables | 96 |
| Alembic migrations | 60 (head: `20260831_bills_payment_method_credit_check`) |
| Primary key strategy | UUID `String(36)` on all entity tables |
| Tenant column | `tenant_id` on ~85 tenant-owned tables |
| Separate `businesses` table | **No** — `tenants` is the business |
| Business types | 13 codes on `tenants.business_type` |
| Platform tables | Master admin, plans, registration, platform audit |

## Architecture in one sentence

Each **Tenant** is one business on the SaaS platform; all operational data is row-scoped by **`tenant_id`**; **`business_type`** on the tenant enables industry modules (KOT, serial/IMEI, travel bookings, etc.) without duplicating core billing tables.

## Documentation map

| Doc | Topic |
|-----|-------|
| [02-database-architecture.md](./02-database-architecture.md) | Layers, PK/FK strategy |
| [03-tenant-architecture.md](./03-tenant-architecture.md) | Isolation model |
| [04-business-type-models.md](./04-business-type-models.md) | All 13 types → modules → tables |
| [05-table-reference.md](./05-table-reference.md) | Table inventory index |
| [05-relationships.md](./05-relationships.md) | Core ER relationships |
| [06-tenant-data-isolation.md](./06-tenant-data-isolation.md) | JWT → repository isolation |
| [07-indexes-and-performance.md](./07-indexes-and-performance.md) | Indexes, dashboard SQL |
| [08-er-diagram.md](./08-er-diagram.md) | ERD index |
| [erd/](./erd/) | Mermaid ERD diagrams |
| [09-migration-strategy.md](./09-migration-strategy.md) | Bootstrap vs upgrade |
| [17-cloud-database-deployment.md](./17-cloud-database-deployment.md) | Cloud readiness |
| [18-backup-and-recovery.md](./18-backup-and-recovery.md) | Backup policy |
| [20-team-database-guide.md](./20-team-database-guide.md) | **Start here for team onboarding** |
| [40-production-readiness-checklist.md](./40-production-readiness-checklist.md) | Go-live checklist |
| [DATABASE-AUDIT-REPORT.md](./DATABASE-AUDIT-REPORT.md) | Full audit findings |

## Schema files

| File | Use |
|------|-----|
| [`../../database/schema.sql`](../../database/schema.sql) | Greenfield full DDL (copy of `backend/sql/02_schema.sql`) |
| `backend/sql/02_schema.sql` | Canonical generated schema |
| `backend/migrations/` | Incremental Alembic upgrades |

## Run integrity report

```bash
cd backend
DATABASE_URL=mysql+pymysql://... python scripts/validate_database_integrity.py
```

## Run isolation tests

```bash
cd backend
pytest tests/test_tenant_isolation.py tests/test_p2_13_tenant_isolation_matrix.py tests/test_biz64_tenant_isolation_regression_suite.py -q
```
