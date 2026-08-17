# SQL & Schema Apply Guide

## Fresh database

1. `01_create_database.sql` — create DB (legacy name `hotel_billing` is OK)
2. `02_schema.sql` — full current schema. It includes SaaS auth, the item
   catalogue and stock-alert fields, category hierarchy protection, billing
   payment/customer fields, WhatsApp and email delivery tables, notifications,
   stock movements, and the current performance indexes.

Optional: `python sql/apply_schema.py` if your ops flow uses that helper.

## Existing database (upgrade)

Prefer **one** of:

### A) Alembic

```bash
cd backend
flask db upgrade
```

Use this path only when the corresponding Alembic revisions are present in
your deployment. The repository's idempotent helper path below is the
authoritative upgrade path for all current schema changes.

### B) Idempotent Python helpers

```bash
cd backend
set DATABASE_URL=mysql+pymysql://...
python scripts/apply_pending_schema.py
```

Runs, in order:

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

## Do not mix blindly

- Do **not** re-run `02_schema.sql` on a production DB (it drops tables).
- Use `02_schema.sql` only for empty/dev rebuilds.
- Keep `02_schema.sql` as the greenfield source of truth whenever you add or
  change tables, columns, constraints, or indexes.

See also: `docs/database-relationships.md`.
