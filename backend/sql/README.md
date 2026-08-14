# SQL & Schema Apply Guide

## Fresh database

1. `01_create_database.sql` — create DB (legacy name `hotel_billing` is OK)
2. `02_schema.sql` — full current schema (includes SaaS auth, `created_by`, `payment_method`, `business_type`, relationship fixes)

Optional: `python sql/apply_schema.py` if your ops flow uses that helper.

## Existing database (upgrade)

Prefer **one** of:

### A) Alembic

```bash
cd backend
flask db upgrade
```

Revisions (in order):

1. `20260326_saas_auth`
2. `20260326_item_created_by`
3. `20260326_bill_payment_method`
4. `20260814_tenant_business_type`
5. `20260814_schema_rel_fixes`
6. `20260814_item_catalog_fields`

### B) Idempotent Python helpers

```bash
cd backend
set DATABASE_URL=mysql+pymysql://...
python scripts/apply_pending_schema.py
```

Runs:

1. `apply_saas_auth_schema.py`
2. `apply_item_created_by.py`
3. `apply_bill_payment_method.py`
4. `apply_tenant_business_type.py`
5. `apply_schema_relationship_fixes.py`
6. `apply_item_catalog_fields.py`

## Do not mix blindly

- Do **not** re-run `02_schema.sql` on a production DB (it drops tables).
- Use `02_schema.sql` only for empty/dev rebuilds.
- Keep `02_schema.sql` as the greenfield source of truth whenever you add columns.

See also: `docs/database-relationships.md`.
