# Deployment Guide — Business Billing

**Canonical deploy doc (Sprint 19).** Older notes: [19-deployment.md](./19-deployment.md).

## Components

1. MySQL 8  
2. Flask API (`/api/v1`) behind Waitress (Windows) or Gunicorn (Linux)  
3. React static build (`frontend/dist`) on Nginx/CDN  
4. SMTP for verification / password reset (optional in local with suppressed mail)

## Local development

### Database

Create DB (default name may be `hotel_billing` — legacy):

- `backend/sql/01_create_database.sql`  
- `backend/sql/02_schema.sql`  
- or `python backend/sql/apply_schema.py`  

Existing DBs: `flask db upgrade` and/or `python backend/scripts/apply_pending_schema.py`.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, CORS_ORIGINS, FRONTEND_URL
python scripts\seed_demo_data.py   # local only
python run.py
```

Health: `http://localhost:5000/api/v1/health`

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
| Migrations | Prefer Flask-Migrate; avoid ad-hoc drift |
| Seed | **Do not** run `seed_demo_data.py` in production |
| Onboarding | `backend/scripts/onboard_tenant.py` or self-serve **Register Business** |
| Suspend | Set `tenants.status` = SUSPENDED |
| Backups | Automated MySQL backups + restore drill |
| Health | `/api/v1/health` and `/health/ready` |

### Backend env (example)

```text
FLASK_ENV=production
SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=mysql+pymysql://user:pass@localhost/hotel_billing
CORS_ORIGINS=https://app.example.com
FRONTEND_URL=https://app.example.com
JWT_ACCESS_TOKEN_EXPIRES=86400
TRUST_PROXY_HEADERS=false

REPORT_TIMEZONE=Asia/Kolkata
FRONTEND_URL=https://app.example.com
MAIL_SUPPRESS_SEND=false
EMAIL_VERIFICATION_REQUIRED=true
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
- Subscription (₹550/mo) is **informational in-app** — commercial activation is offline/contact  

## Related

- [production readiness](./21-production-readiness.md)  
- [security](./17-security.md)  
- Root [README.md](../README.md)  
