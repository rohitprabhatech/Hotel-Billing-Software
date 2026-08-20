# Deployment Guide — Business Billing

**Canonical deploy doc.** Older notes: [19-deployment.md](./19-deployment.md).  
**Schema status:** 23 app tables in `02_schema.sql`; hosted DB stamped `20260818_phase8_saas`. See [database-design.md](./database-design.md) and [backup-and-recovery.md](./backup-and-recovery.md).

## Components

1. MySQL 8 / MariaDB (Hostinger live is MariaDB)  
2. Flask API (`/api/v1`) behind Waitress (Windows) or Gunicorn (Linux)  
3. React static build (`frontend/dist`) on Nginx/CDN  
4. SMTP for verification / password reset (optional in local with suppressed mail)

## Local development

### Database

**Empty DB only:**

- `backend/sql/01_create_database.sql`  
- `backend/sql/02_schema.sql`  
- or `python backend/sql/apply_schema.py`  

**Existing DBs:** inspect first, then:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out schema-report.json
.\.venv\Scripts\python.exe scripts\apply_pending_schema.py
.\.venv\Scripts\python.exe scripts\stamp_alembic_head.py
```

**Never** re-run `02_schema.sql` on a database that already has live data. Do **not** apply `03_saas_auth_alter.sql`. Do **not** `flask db upgrade` from an empty `alembic_version` on live.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Set DATABASE_URL or MYSQL_*, SECRET_KEY, JWT_SECRET_KEY, CORS_ORIGINS, FRONTEND_URL
python scripts\seed_demo_data.py   # local only
python run.py
```

Health: `http://localhost:5000/api/v1/health` (or the port in `run.py`)

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
# VITE_API_BASE_URL=http://localhost:5000/api/v1
npm run dev
```

UI: `http://localhost:5173`

## Production checklist

| Item | Guidance |
|------|----------|
| Secrets | Strong `SECRET_KEY` / `JWT_SECRET_KEY`; never commit `.env` |
| CORS | Exact app origins only |
| HTTPS | Terminate TLS at reverse proxy |
| Migrations | Inspect → backup → `apply_pending_schema.py` → `stamp_alembic_head.py`. Never `02_schema.sql` on production |
| Master Admin | `check_platform_ready.py`, then `.\.venv\Scripts\python.exe scripts\seed_master_admin.py` with `MASTER_ADMIN_EMAIL` / `MASTER_ADMIN_PASSWORD` (do not commit). If `master_admins` is still 0, seed has not succeeded. |
| Seed demo | **Do not** run `seed_demo_data.py` in production |
| Onboarding | `backend/scripts/onboard_tenant.py` or self-serve **Register Business** |
| Suspend account | Master **Deactivate** → `tenants.status` = SUSPENDED |
| Suspend billing | Master **Suspend** → `subscriptions.status` = SUSPENDED (login allowed, API 402) |
| Backups | Automated MySQL backups + restore drill |
| Health | `/api/v1/health` and `/health/ready` |

### Backend env (example)

```text
FLASK_ENV=production
SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=mysql+pymysql://user:pass@localhost/hotel_billing
# Or split fields (used when DATABASE_URL is empty): MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT
CORS_ORIGINS=https://app.example.com
FRONTEND_URL=https://app.example.com
JWT_ACCESS_TOKEN_EXPIRES=86400
TRUST_PROXY_HEADERS=false

REPORT_TIMEZONE=Asia/Kolkata
MAIL_SUPPRESS_SEND=false
EMAIL_VERIFICATION_REQUIRED=true

# Master seed only (do not commit real values)
# MASTER_ADMIN_EMAIL=
# MASTER_ADMIN_PASSWORD=
# MASTER_ADMIN_NAME=Prabha Technology Admin
```

Set `TRUST_PROXY_HEADERS=true` only when a trusted reverse proxy strips/forges `X-Forwarded-For`. Prefer JWT access TTL of 8–12 hours in production; logout revokes tokens via `token_version`.

### Frontend build

```text
VITE_API_BASE_URL=https://api.example.com/api/v1
npm ci && npm run build
# Serve dist/ over HTTPS
```

### Process examples

```text
# Windows
waitress-serve --listen=0.0.0.0:5000 wsgi:app

# Linux
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Multi-tenant ops

- Each customer = one **tenant** (business)  
- Never share credentials across businesses  
- Public register is **pending until Master approval**  
- Subscription prices on the landing page come from the plan catalog; commercial activation is offline/contact  
- Deactivate a tenant to block login without deleting bills  

## Related

- [backup-and-recovery.md](./backup-and-recovery.md)  
- [master-admin-manual.md](./master-admin-manual.md)  
- [database-design.md](./database-design.md)  
- [production readiness](./21-production-readiness.md)  
- [security-architecture.md](./security-architecture.md)  
- Root [README.md](../README.md)  
