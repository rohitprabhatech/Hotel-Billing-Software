# Production Readiness

**Canonical release gate:** [final-qa-report.md](./final-qa-report.md) (Sprint 22).  
**Deploy steps:** [deployment-guide.md](./deployment-guide.md).  
**Security:** [security-tenant-audit.md](./security-tenant-audit.md).

## Regression

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```

```powershell
cd frontend
npm run build
```

Expect: all tests green; Vite build succeeds.

## Security checklist

- [ ] `FLASK_ENV=production`
- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY` (32+ chars; not defaults)
- [ ] `DEBUG` off (ProductionConfig)
- [ ] HTTPS at reverse proxy
- [ ] `CORS_ORIGINS` = real frontend only
- [ ] `TRUST_PROXY_HEADERS=true` only behind a trusted proxy
- [ ] Least-privilege MySQL user
- [ ] `.env` not committed; backups in place
- [ ] No hard-delete APIs for bills/audit
- [ ] Tenant isolation + security tests passing
- [ ] Billing users cannot access reports / audit / AI / users admin
- [ ] `ALLOW_DEV_AUTH_TOKENS` false (forced in production)
- [ ] Prefer JWT access TTL 8–12h; logout revokes via `token_version`

## Staging pilot (one business)

1. Apply schema / migrations  
2. Onboard via **Register Business** or `scripts/onboard_tenant.py`  
3. Owner: categories, items, billing user  
4. Billing: create, print, cancel test bills (Cash + Online)  
5. Owner: dashboard, reports export, AI, audit  
6. Second business isolation smoke  
7. Confirm thermal/browser print on counter device  

## Onboarding a new business

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\onboard_tenant.py `
  --business-name "Sunrise Retail" `
  --name "Sunrise Retail" `
  --owner-name "Owner Name" `
  --owner-email "owner@sunrise.example" `
  --owner-password "StrongPass@123" `
  --city "Pune" `
  --phone "9000000000" `
  --billing-name "Counter 1" `
  --billing-email "billing@sunrise.example" `
  --billing-password "StrongPass@123"
```

Demo seed (**local only**): `python scripts\seed_demo_data.py`

## Runtime

```powershell
# Backend (Windows)
waitress-serve --listen=0.0.0.0:5000 wsgi:app

# Frontend
npm ci && npm run build
# Serve dist/ over HTTPS
```

Health: `GET /api/v1/health` · `GET /api/v1/health/ready`

## Subscription note

In-app plan is **₹550 / month informational** — no payment gateway. Activate commercially offline via Prabha Technology support.
