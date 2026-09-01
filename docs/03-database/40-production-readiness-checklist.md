# Production Database Readiness Checklist

Use before go-live and after major schema changes.

## Architecture & models

- [x] All models reviewed (~95 classes, 96 tables)
- [x] Shared vs industry tables documented
- [x] No duplicate per-business customer/item tables
- [x] Primary key strategy documented (UUID)

## Isolation & security

- [x] Tenant isolation verified (pytest isolation suite)
- [x] JWT → repository tenant_id filtering confirmed
- [ ] Item image file endpoint risk accepted or mitigated
- [x] No DB credentials in source control
- [x] Production secret validation in `ProductionConfig`

## Relationships & integrity

- [x] Core FK relationships documented
- [x] Delete strategy documented (cancel/deactivate vs hard delete)
- [x] Bill numbering uses DB lock (`FOR UPDATE`)
- [x] Financial totals computed in service layer

## Inventory

- [x] Stock deduction timing documented
- [x] Stock movement audit trail (`stock_movements`)
- [x] Concurrent stock updates use row locks

## Migrations & schema

- [x] 60 Alembic revisions; head `20260831_bills_payment_method_credit_check`
- [x] `database/schema.sql` available for greenfield
- [ ] Staging `flask db upgrade` run on production clone
- [ ] `alembic_version` matches deployed code tag

## Performance

- [x] Pagination on major list APIs
- [x] Dashboard/report aggregations use SQL SUM/COUNT
- [x] Performance indexes migration present
- [ ] EXPLAIN run on slow reports under load (ops)

## Operations

- [x] Connection pooling configured (`SQLALCHEMY_ENGINE_OPTIONS`)
- [x] Cloud deployment guide written
- [x] Backup/recovery guide written
- [x] Integrity validation script: `validate_database_integrity.py`

## Documentation

- [x] DATABASE-AUDIT-REPORT.md
- [x] Team guide (20-team-database-guide.md)
- [x] ERD diagrams (erd/)
- [x] Business type → models mapping

## Tests

- [x] Tenant isolation tests (40+ files)
- [ ] Full `pytest` pass on release branch
- [ ] Manual smoke: bill + purchase + cancel on staging

## Sign-off

| Role | Name | Date | Pass |
|------|------|------|------|
| Backend lead | | | |
| DBA / Ops | | | |
| Product owner | | | |
