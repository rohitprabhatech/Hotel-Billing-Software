# Business Billing

Multi-tenant billing SaaS for restaurants, hotels, retail, grocery, and more.  
**Owner** + **Billing User** + **Master Admin** (platform) · Provider: **Prabha Technology Pvt. Ltd.**

> Repository folder may still say `Hotel-Billing-Software`; the product name is **Business Billing**.

## Stack

- **Backend:** Flask, SQLAlchemy, JWT, MySQL  
- **Frontend:** React, MUI, Vite, Axios  

## Quick start (local)

### 1) Database

Create MySQL database (default name `hotel_billing`) **only for empty local installs**, then apply:

- `backend/sql/01_create_database.sql`  
- `backend/sql/02_schema.sql`  

Or: `python backend/sql/apply_schema.py`

**Existing / hosted databases:** inspect, backup, then `python backend/scripts/apply_pending_schema.py`. Never re-run `02_schema.sql` on live data. See [`docs/backup-and-recovery.md`](docs/backup-and-recovery.md).

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

### Demo logins (seed)

| Role | Email | Password |
|------|-------|----------|
| Owner (Business A) | owner@hotela.com | Owner@12345 |
| Billing (Business A) | billing@hotela.com | Billing@12345 |

## Tests

```powershell
cd backend
.\.venv\Scripts\python -m pytest
```

## Docs

Start at [`docs/README.md`](docs/README.md) — single structured system:

`00-project-foundation` · `01-requirements` · `02-architecture` · `03-database` · `04-common-modules` · **`05-businesses` (14 packs)** · `06-master-admin` · `07-api` · `08-ui-ux` · `09-subscription` · `10-testing` · `11-user-manual` · `12-testing-guides` · `13-phases` · `14-sprints` · `archive/`

Status: [`docs/software-status.md`](docs/software-status.md) (living code progress) · [`docs/documentation-status.md`](docs/documentation-status.md) · Tracker: [`docs/14-sprints/sprint-tracker.md`](docs/14-sprints/sprint-tracker.md)

Historical Phase/Sprint reports: [`docs/archive/`](docs/archive/).

## Production

Follow archived ops notes under [`docs/archive/flat-root/deployment-guide.md`](docs/archive/flat-root/deployment-guide.md) and [`docs/archive/flat-root/21-production-readiness.md`](docs/archive/flat-root/21-production-readiness.md) until promoted into phase/sprint docs.  
Onboard real businesses with **Register Business** (Master must **approve**) or `backend/scripts/onboard_tenant.py` (not the demo seeder).

**Hosted schema (current):** Phase 8 tables are present; Alembic stamped `20260818_phase8_saas`.  
**Open ops:** if `check_platform_ready.py` reports `master_admins: 0`, set `MASTER_ADMIN_*` in `backend/.env` and run:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

Then `/master/login` via the landing footer dot. See [`docs/11-user-manual/04-master-admin-manual.md`](docs/11-user-manual/04-master-admin-manual.md).

**Plan:** Landing prices come from the plan catalog. No in-app payment gateway — contact Prabha Technology to activate.
