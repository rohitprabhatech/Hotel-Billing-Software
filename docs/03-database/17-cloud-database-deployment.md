# Cloud Database Deployment

## Target databases

Primary: **MySQL 8.x** (InnoDB, utf8mb4)

Supported via SQLAlchemy URL: `mysql+pymysql://...`

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Production yes | Full URL e.g. `mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4` |
| `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | Alternative | Used if `DATABASE_URL` unset |
| `FLASK_ENV` | Yes | `production` enables secret validation |
| `SECRET_KEY`, `JWT_SECRET_KEY` | Yes | 32+ chars |
| `DB_POOL_SIZE` | Optional | Default 5 |
| `DB_POOL_MAX_OVERFLOW` | Optional | Default 10 |
| `DB_POOL_RECYCLE` | Optional | Default 280 seconds |
| `DB_POOL_TIMEOUT` | Optional | Default 30 seconds |
| `REPORT_TIMEZONE` | Optional | Default `Asia/Kolkata` |

**Never commit credentials.** Use platform secret managers.

## Recommended production pool sizing

| Traffic | pool_size | max_overflow |
|---------|-----------|--------------|
| Small (< 20 concurrent) | 5 | 10 |
| Medium | 10 | 20 |
| High | 15–20 | 30 |

Monitor connection count vs provider limit (RDS `max_connections`).

## SSL/TLS

For managed MySQL (RDS, PlanetScale, Azure):

```
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4&ssl_ca=/path/to/ca.pem
```

Or provider-specific SSL params in `connect_args` if needed.

## Deployment steps

1. Provision MySQL instance (private network preferred)
2. Create database + least-privilege user (SELECT, INSERT, UPDATE, DELETE, DDL for migrations only on deploy role)
3. Set `DATABASE_URL` in hosting platform
4. **Backup** empty instance (baseline)
5. Bootstrap:
   - **New:** apply `database/schema.sql` OR run migrations from stamped baseline
   - **Existing:** `flask --app run:app db upgrade` only
6. Run `python scripts/validate_database_integrity.py`
7. Seed master admin if SaaS: `python scripts/seed_master_admin.py`
8. Smoke test tenant register → login → create bill

## Hosting checklist

- [ ] DB not publicly open (VPC / IP allowlist)
- [ ] Automated daily backups enabled
- [ ] `FLASK_ENV=production`
- [ ] Strong secrets set
- [ ] Connection pool env tuned
- [ ] Migrations tested on staging clone
- [ ] Timezone documented for reports (`REPORT_TIMEZONE`)

## Providers (examples)

Works with: AWS RDS, Google Cloud SQL, Azure Database for MySQL, Railway, Render, DigitalOcean Managed MySQL.

Application backend and DB should be in same region for latency.
