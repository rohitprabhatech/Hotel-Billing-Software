# Database — Production Schema & Ops

Canonical SQL and migration tooling live under **`backend/sql/`** and **`backend/migrations/`**.

| Artifact | Path | Purpose |
|----------|------|---------|
| **Greenfield schema (96 tables)** | [`schema.sql`](./schema.sql) | Copy of `backend/sql/02_schema.sql` — full MySQL DDL for empty DB |
| Create database | `backend/sql/01_create_database.sql` | Creates `hotel_billing` database |
| Apply helper | `backend/sql/apply_schema.py` | Applies schema to `DATABASE_URL` |
| Regenerate schema | `backend/scripts/regenerate_02_schema.py` | Rebuild `02_schema.sql` from models |
| Alembic migrations | `backend/migrations/versions/` | 60 incremental revisions (head: `20260831_bills_payment_method_credit_check`) |
| Schema inspection | `backend/scripts/inspect_database_schema.py` | Read-only metadata report |
| Integrity validation | `backend/scripts/validate_database_integrity.py` | Report-only orphan/duplicate checks |

## Greenfield bootstrap

```bash
# 1. Create DB (MySQL)
mysql -u root -p < backend/sql/01_create_database.sql

# 2. Apply full schema (DESTRUCTIVE — empty DB only)
python backend/sql/apply_schema.py

# 3. Stamp Alembic head, then upgrade if needed
cd backend
flask --app run:app db stamp 20260831_bills_payment_method_credit_check
flask --app run:app db upgrade
```

## Hosted / existing DB

Never run `schema.sql` on production with data. Use:

```bash
cd backend
flask --app run:app db current
flask --app run:app db upgrade
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Full SQLAlchemy URL (preferred in cloud) |
| `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | Split MySQL config |
| `DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_TIMEOUT` | Connection pool |
| `REPORT_TIMEZONE` | Tenant reporting timezone (default `Asia/Kolkata`) |

**Never commit credentials.** Use platform secrets (Railway, Render, RDS, Azure, etc.).

## Documentation

Full audit and team guides: [`docs/03-database/`](../docs/03-database/)

- [`DATABASE-AUDIT-REPORT.md`](../docs/03-database/DATABASE-AUDIT-REPORT.md) — latest audit
- [`20-team-database-guide.md`](../docs/03-database/20-team-database-guide.md) — explain to dev team
- [`erd/`](../docs/03-database/erd/) — Mermaid ERD diagrams
