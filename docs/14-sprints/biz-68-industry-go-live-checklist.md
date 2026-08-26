# Industry Packs — Go-Live Checklist (BIZ-68)

**Product:** Business Billing  
**Scope:** All **14** supported business types (Medical Store / pharmacy **excluded**)  
**Alembic head:** `20260826_biz66_perf_indexes`  
**Date:** 2026-08-26  

Sign this checklist before enabling industry tenants on production. Platform baseline (auth, billing, Master Admin, subscriptions) is assumed live.

---

## 0. Preconditions

| # | Item | Owner | Done |
|---|------|-------|------|
| 0.1 | BIZ-67 ops runbook reviewed | Ops | ☐ |
| 0.2 | Staging `flask db upgrade` to head completed | Ops | ☐ |
| 0.3 | Backup of production DB verified (restore drill or host panel) | Ops | ☐ |
| 0.4 | Medical / pharmacy features confirmed **not** in catalog | Product | ☐ |

Related: [`../03-database/10-industry-modules-ops-runbook.md`](../03-database/10-industry-modules-ops-runbook.md)

---

## 1. Security

| # | Item | Done |
|---|------|------|
| 1.1 | `FLASK_ENV=production`; `DEBUG` off | ☐ |
| 1.2 | Strong `SECRET_KEY` / `JWT_SECRET_KEY` (32+; not repo defaults) | ☐ |
| 1.3 | HTTPS at reverse proxy; `CORS_ORIGINS` = real frontend only | ☐ |
| 1.4 | `TRUST_PROXY_HEADERS=true` only behind trusted proxy | ☐ |
| 1.5 | Least-privilege MySQL user; `.env` not in git | ☐ |
| 1.6 | `ALLOW_DEV_AUTH_TOKENS` false in production | ☐ |
| 1.7 | BIZ-64 isolation suite green on CI/staging | ☐ |
| 1.8 | BIZ-65 audit scrub + Owner-only audit access confirmed | ☐ |
| 1.9 | Billing users cannot access reports / audit / users admin | ☐ |

---

## 2. Backup & recovery

| # | Item | Done |
|---|------|------|
| 2.1 | Host mysqldump / panel backup taken; location recorded | ☐ |
| 2.2 | Optional JSON inventory: `python scripts/backup_database.py` | ☐ |
| 2.3 | Schema inspect saved: `python scripts/inspect_database_schema.py --json-out pre-golive.json` | ☐ |
| 2.4 | Restore procedure known (host restore — no “reset production” script) | ☐ |
| 2.5 | **Never** run `sql/02_schema.sql` on live data | ☐ |

---

## 3. Monitoring & health

| Probe | Expect | Wire at |
|-------|--------|---------|
| `GET /api/v1/health` | 200, `status: ok` | Load balancer / uptime |
| `GET /api/v1/health/ready` | 200 when DB up; 503 if DB down | Load balancer readiness |

| # | Item | Done |
|---|------|------|
| 3.1 | Both probes configured in reverse proxy / uptime tool | ☐ |
| 3.2 | Alert on sustained `/health/ready` 503 | ☐ |
| 3.3 | App + waitress/gunicorn process supervised (restart policy) | ☐ |
| 3.4 | Disk space for uploads / PDF temp watched | ☐ |

---

## 4. Support scripts inventory

| Script | Purpose | Prod-safe? |
|--------|---------|------------|
| `check_platform_ready.py` | Phase 8 tables + master admin readiness | Yes (read-only) |
| `inspect_database_schema.py` | Schema snapshot JSON | Yes (read-only) |
| `print_alembic_chain.py` | Print linear revision order | Yes (local) |
| `backup_database.py` | JSON metadata dump to `backend/backups/` | Yes (read; not a full mysqldump) |
| `onboard_tenant.py` | Create tenant + owner (+ optional billing) | Yes (with approval) |
| `seed_master_admin.py` | First Master Admin | Once / with approval |
| `stamp_alembic_head.py` | Stamp Phase 8 only | Legacy catch-up |
| `stamp_alembic_industry_head.py` | Stamp industry head if tables exist | Catch-up only |
| `apply_pending_schema.py` + `apply_*.py` | Legacy idempotent helpers | Prefer Alembic for industry |
| `apply_perf_indexes.py` | Index catch-up | Optional after BIZ-66 |
| `check_subscription_expiry.py` | Subscription notices job | Scheduled ops |
| `seed_demo_data.py` | Demo seed | **Local only** |

---

## 5. Industry enablement (per business type)

Enable **one pilot tenant at a time** via `business_type` (module flags). Smoke Owner + Billing for each pack before bulk flips.

| Business | Prior gate / proof | Pilot smoke | Done |
|----------|-------------------|-------------|------|
| Hotels / Restaurants | BIZ-19 F&B gate | Tables → order → KOT → settle bill | ☐ |
| Cafes / Tea | Shared F&B + cafe | Quick POS / addons | ☐ |
| Grocery / Kirana | BIZ-24 | Barcode POS + credit | ☐ |
| Clothing | BIZ-28 | Variants POS + return | ☐ |
| Mobile | BIZ-34 | Serial sell + repair | ☐ |
| Electronics | BIZ-34 | Serial + installation | ☐ |
| Hardware | BIZ-39 | UoM POS + quote/challan | ☐ |
| Building material | BIZ-39 | Warehouse + challan | ☐ |
| Bakery / Sweet | BIZ-43 | Production + cake order | ☐ |
| Stationery | BIZ-46 | Search POS | ☐ |
| Book stores | BIZ-46 | ISBN + return | ☐ |
| Furniture | BIZ-50 | Custom order + delivery | ☐ |
| Wholesale | BIZ-55 | Price list + SO/PO | ☐ |
| Travel agencies | BIZ-60 | Package + booking + agent | ☐ |
| **Medical / pharmacy** | — | **OUT OF SCOPE — do not enable** | N/A |

Cross-cutting: BIZ-61 reports, BIZ-62 AI insights, BIZ-63 notifications, BIZ-64 isolation, BIZ-65 audit, BIZ-66 perf indexes.

---

## 6. API / UI smoke (production or staging twin)

| # | Check | Done |
|---|-------|------|
| 6.1 | `GET /api/v1/health` and `/health/ready` | ☐ |
| 6.2 | Owner login → dashboard → create category/item → bill | ☐ |
| 6.3 | Billing user: bill create/print; blocked from audit | ☐ |
| 6.4 | Second tenant: cannot read first tenant IDs (404) | ☐ |
| 6.5 | Pilot industry page loads (lazy route) without console errors | ☐ |
| 6.6 | Frontend production build: `npm run build` | ☐ |
| 6.7 | Notification bell receives a known event (e.g. low stock / KOT ready) | ☐ |
| 6.8 | Audit log shows create/update for pilot action | ☐ |

---

## 7. Final regression commands

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_biz64_tenant_isolation_regression_suite.py tests/test_biz67_migration_ops_runbook.py tests/test_biz68_production_readiness_gate.py tests/test_health.py -q

cd ..\frontend
npm run build
```

Full suite optional before major releases: `pytest -q` (long).

---

## 8. Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Ops | | | |
| Product / Business | | | |
| Engineering | | | |

**Medical Store remains excluded.** Program complete pending business approval of this checklist.

Gate report: [`biz-68-production-readiness-gate-report.md`](./biz-68-production-readiness-gate-report.md)
