# Sprint P8-2 Completion Report — Master Admin auth + dashboard foundation

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Platform Master Admin is a **separate identity** from Owner/Billing User. Backend rejects Owner access to `/api/v1/master/*` with **403** (not by hiding UI). Master JWT has **no** `tenant_id` and cannot call tenant APIs.

## Database changes

| Change | Notes |
|--------|--------|
| Table `master_admins` | `id`, `name`, `email` unique, `password_hash`, `is_active`, `token_version`, `last_login_at` |
| `backend/sql/02_schema.sql` | CREATE + DROP |
| `backend/scripts/apply_master_admins.py` | Idempotent; listed in `apply_pending_schema.py` |

**No** existing tenant/user/bill tables altered. **No** data deleted.

Bootstrap (existing DB):

```text
cd backend
python -c "from dotenv import load_dotenv; load_dotenv(); import runpy; raise SystemExit(runpy.run_path('scripts/apply_master_admins.py')['main']())"
# then set MASTER_ADMIN_EMAIL / MASTER_ADMIN_PASSWORD in .env
python scripts/seed_master_admin.py
```

## API changes

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/login` | Public — tenant **or** master |
| POST | `/api/v1/auth/logout` | `session_required` (tenant or master) |
| GET | `/api/v1/auth/me` | `session_required` |
| POST | `/api/v1/auth/change-password` | `session_required` |
| GET | `/api/v1/master/dashboard/summary` | `master_required` |

Master login user payload: `role=MASTER_ADMIN`, `tenant=null`.  
Dashboard summary: `total_businesses`, `active_businesses`, `suspended_businesses` from real `tenants` rows.

Owner/Billing hitting master summary → **403 FORBIDDEN**.  
Master hitting `/api/v1/bills` → **403** `"Master admin cannot access tenant APIs"`.

## Frontend changes

| Path | Change |
|------|--------|
| `authRouting.js` | `MASTER_ADMIN` → `/master/dashboard` |
| `paths.js` / `AppRoutes.jsx` | `/master/*` + `ProtectedRoute roles={['MASTER_ADMIN']}` |
| `layouts/MasterLayout.jsx` | **New** — not OwnerLayout |
| `pages/master/MasterDashboardPage.jsx` | Live KPIs |
| `services/masterService.js` | Summary client |
| `ChangePasswordPage.jsx` | Cancel path for master |

Owner/Billing layouts unchanged (no Master nav mixed in).

## Tests

`pytest tests/test_p8_2_master_auth.py` plus existing auth/isolation suite (run in this sprint).

## Known issues / residuals

- Registration approval is P8-3 (complete).
- No trial/plans/subscriptions yet (P8-4…P8-6).
- Master login is not written to tenant `audit_logs` (needs `platform_audit_logs` later).
- Seed credentials must come from env — never commit production passwords.

---

**Stopped.** Should I start the next sprint?
