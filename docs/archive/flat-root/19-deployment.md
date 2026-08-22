# 19 — Deployment

## Environments

| Env | Purpose |
|-----|---------|
| Local | Developer machines |
| Staging | Pre-production verification |
| Production | Live hotels |

## Runtime Components

1. MySQL 8
2. Flask API (WSGI: waitress/gunicorn as appropriate for OS)
3. React static build served by Nginx or similar
4. Environment configuration

## Backend Deploy Steps

```text
1. Provision MySQL database
2. Set environment variables
3. python -m venv && pip install -r requirements.txt
4. flask db upgrade
5. seed roles (+ controlled tenant/owner if needed)
6. start WSGI process behind reverse proxy
```

## Frontend Deploy Steps

```text
1. Set VITE_API_BASE_URL (e.g. https://api.example.com/api/v1)
2. npm ci && npm run build
3. Serve dist/ over HTTPS
```

## Windows Production Process (optional)

```text
waitress-serve --listen=0.0.0.0:5000 wsgi:app
```

Linux/macOS typically use gunicorn with `wsgi:app`.

## Environment Variables (Backend)

```text
FLASK_ENV=production
SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=mysql+pymysql://user:pass@localhost/hotel_billing
CORS_ORIGINS=https://app.example.com
JWT_ACCESS_TOKEN_EXPIRES=86400
REPORT_TIMEZONE=Asia/Kolkata
```

## Reverse Proxy

- Terminate TLS
- Forward to Flask
- Serve frontend static files
- Security headers (basic)

## Database

- Automated backups
- Migration discipline via Flask-Migrate only
- Least-privilege DB user for app

## Health Checks

- `GET /api/v1/health` — process up
- `GET /api/v1/health/ready` — DB connectivity

## Multi-Tenant Ops Notes

- New hotel = controlled onboarding via `backend/scripts/onboard_tenant.py`
- Suspend via `tenants.status`
- Never share credentials across hotels
- Do not use `seed_demo_data.py` in production

## Printing in Production

- Client workstations use browser print to thermal printer
- Test 58mm/80mm CSS on target hardware during rollout

## Rollback

- Keep previous app artifact
- DB migrations must be backward-safe or have documented down migration
