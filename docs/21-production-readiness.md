# 21 — Production Readiness (Sprint 9)

## Regression Status

Run from `backend/`:

```bash
.\.venv\Scripts\python -m pytest
```

Expected: all tests green (auth, isolation, billing, GST, cancel, print, reports/export, audit).

## Security Checklist

- [ ] `FLASK_ENV=production`
- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY` (32+ random chars; not repo defaults)
- [ ] `DEBUG` off (enforced by ProductionConfig)
- [ ] HTTPS terminated at reverse proxy
- [ ] `CORS_ORIGINS` limited to real frontend origin(s)
- [ ] MySQL user is least-privilege (no SUPER)
- [ ] `.env` not committed; backups encrypted where practical
- [ ] No hard-delete APIs for bills/audit logs
- [ ] Tenant isolation tests passing
- [ ] Billing users cannot access `/reports` or `/audit-logs`

Production config refuses weak/default secrets at startup.

## Staging Pilot Checklist (one hotel)

1. Create/verify MySQL database `hotel_billing`
2. Apply schema (`backend/sql/02_schema.sql` or migrations)
3. Onboard tenant via `scripts/onboard_tenant.py`
4. Owner adds categories/items
5. Billing user creates, prints, and cancels a test bill
6. Owner verifies dashboard, reports export, and audit log
7. Confirm thermal print 58mm/80mm on counter printer

## Onboarding a New Hotel

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\onboard_tenant.py `
  --business-name "Hotel Sunrise" `
  --name "Hotel Sunrise" `
  --owner-name "Owner Name" `
  --owner-email "owner@hotelsunrise.com" `
  --owner-password "StrongPass@123" `
  --city "Pune" `
  --phone "9000000000" `
  --gst-number "27XXXXX..." `
  --billing-name "Counter 1" `
  --billing-email "billing@hotelsunrise.com" `
  --billing-password "StrongPass@123"
```

Demo seed (local only): `python scripts\seed_demo_data.py`

## Runtime Commands

### Backend (Windows-friendly)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
# development
python run.py
# production-style
pip install waitress
waitress-serve --listen=0.0.0.0:5000 wsgi:app
```

### Frontend

```powershell
cd frontend
# set VITE_API_BASE_URL in .env
npm ci
npm run build
# serve dist/ behind Nginx/IIS/Caddy with HTTPS
```

## Health

- `GET /api/v1/health` → process alive
- `GET /api/v1/health/ready` → database reachable

## Manual Smoke (billing path)

1. Login owner → create category/item
2. Login billing → new bill → generate → print
3. Cancel with reason → confirm bill still visible
4. Owner reports export xlsx
5. Owner audit shows CREATE_BILL / PRINT_BILL / CANCEL_BILL
