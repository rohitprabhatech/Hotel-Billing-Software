# Backup & Recovery

## Policy (recommended)

| Item | Recommendation |
|------|----------------|
| Frequency | Daily automated snapshots minimum |
| Retention | 7–30 days rolling; monthly archive for compliance |
| Pre-migration | Manual snapshot before every `flask db upgrade` on production |
| Pre-deploy | Snapshot before major releases |
| Test restore | Quarterly restore drill to staging |

## What to backup

- Full MySQL database (all 96+ tables including `alembic_version`)
- Uploaded files: `ITEM_IMAGE_UPLOAD_DIR` (not in DB BLOBs)
- Environment secrets (stored in secret manager, not in backup dump)

## Managed cloud backup

### AWS RDS
- Enable automated backups + PITR
- Restore to new instance → update `DATABASE_URL` → verify → switch

### Other providers
Use native snapshot/backup features; document RTO/RPO per provider.

## Manual backup (ops)

```bash
mysqldump -h HOST -u USER -p --single-transaction --routines --triggers hotel_billing > backup_YYYYMMDD.sql
```

Restore (staging only until verified):

```bash
mysql -h HOST -u USER -p hotel_billing < backup_YYYYMMDD.sql
```

## Recovery procedure

1. Stop application traffic (maintenance mode)
2. Restore DB to point-in-time or snapshot
3. Run `flask db current` — ensure `alembic_version` matches expected code
4. Run `validate_database_integrity.py`
5. Smoke test: login, list bills, create test bill on staging tenant
6. Resume traffic

## What backups do NOT fix

- Corrupted application code — use git rollback
- Leaked secrets — rotate keys after incident
- Deleted uploaded images — backup upload directory separately

## Before first production migration

1. Full backup
2. Clone to staging
3. Run migration on clone
4. Run full pytest + manual billing smoke
5. Then migrate production
