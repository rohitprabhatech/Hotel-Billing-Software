# Hotel Billing Software

Multi-tenant hotel/restaurant billing SaaS (Owner + Billing User).

## Stack

- Backend: Flask, SQLAlchemy, JWT, MySQL
- Frontend: React, MUI, Vite, Axios

## Quick Start (Local)

### 1) Database

Create MySQL DB `hotel_billing`, then apply:

- `backend/sql/01_create_database.sql`
- `backend/sql/02_schema.sql`

Or run: `python backend/sql/apply_schema.py`

### 2) Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # set DATABASE_URL / secrets
python scripts\seed_demo_data.py
python run.py
```

API: `http://localhost:5000/api/v1/health`

### 3) Frontend

```powershell
cd frontend
npm install
copy .env.example .env   # VITE_API_BASE_URL=http://localhost:5000/api/v1
npm run dev
```

UI: `http://localhost:5173`

### Demo logins

| Role | Email | Password |
|------|-------|----------|
| Owner A | owner@hotela.com | Owner@12345 |
| Billing A | billing@hotela.com | Billing@12345 |

## Tests

```powershell
cd backend
.\.venv\Scripts\python -m pytest
```

## Docs

See `docs/` (architecture, API, billing, security, deployment, production readiness).

## Production / Staging

Follow `docs/19-deployment.md` and `docs/21-production-readiness.md`.  
Onboard real hotels with `backend/scripts/onboard_tenant.py` (not the demo seeder).
