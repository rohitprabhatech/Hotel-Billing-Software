# Sprint P8-3 Completion Report — Business registration approval

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Public **Register Business** no longer creates a live tenant. Signups land in `registration_requests` as **PENDING**. Master Admin approves or rejects from `/master/registration-requests`. Approve creates an **ACTIVE** tenant and an owner who can **log in immediately** (`email_verified=True`). Existing seed tenants stay ACTIVE (grandfathered).

## Database changes

| Change | Notes |
|--------|--------|
| Table `registration_requests` | Owner/business fields, `password_hash` (never returned), `status`, timestamps, `approved_by` / `rejected_by` → `master_admins`, optional `tenant_id`, `terms_accepted_at` |
| `backend/sql/02_schema.sql` | CREATE + DROP (drop before `master_admins`) |
| `backend/scripts/apply_registration_requests.py` | Idempotent; listed after `apply_master_admins.py` |

**No** existing tenant/user/bill tables altered. **No** data deleted. Tenant `status` CHECK is unchanged (`ACTIVE` \| `SUSPENDED`) — pending businesses are **not** tenant rows.

Bootstrap (existing DB):

```text
cd backend
python -c "from dotenv import load_dotenv; load_dotenv(); import runpy; raise SystemExit(runpy.run_path('scripts/apply_registration_requests.py')['main']())"
```

Or run `scripts/apply_pending_schema.py` (includes this helper).

## API changes

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/register-business` | Public — **PENDING** request; requires `terms_accepted: true`; no JWT |
| GET | `/api/v1/master/registration-requests` | `master_required` |
| GET | `/api/v1/master/registration-requests/<id>` | `master_required` |
| POST | `/api/v1/master/registration-requests/<id>/approve` | `master_required` |
| POST | `/api/v1/master/registration-requests/<id>/reject` | `master_required` — `{ "reason": "..." }` min 8 chars |
| GET | `/api/v1/master/dashboard/summary` | Adds `pending_requests` |

Submit response: `message`, `request_id`, `status`, `owner_email`, `business_name`, `business_type`. **No** `tenant_id`, **no** `verification_token`, **no** password.

Pending login (correct password, not yet approved) → **401** `"Your registration request is pending approval by Prabha Technology."`  
Owner/Billing hitting Master APIs → **403**.  
Rejected emails may submit again. Duplicate **PENDING** email → **409**.

## Frontend changes

| Path | Change |
|------|--------|
| `RegisterBusinessPage.jsx` | Required Terms/Privacy checkbox; success copy; **no** auto-login / verify-email redirect |
| `MasterLayout.jsx` | Nav: Registration requests |
| `pages/master/MasterRegistrationRequestsPage.jsx` | List/filter/view/approve/reject |
| `MasterDashboardPage.jsx` | Pending requests KPI |
| `services/masterService.js` | Request APIs |

Owner/Billing layouts unchanged.

## Emails

- Received (on submit)  
- Approved (login URL)  
- Rejected (includes reason)  
- `verify_email.html` copy is for **email change**, not signup

## Tests

`pytest tests/test_p8_3_registration_approval.py` plus updated registration/isolation/report helpers (`terms_accepted` + Master approve instead of verify-email).

## Known issues / residuals

- Trial / plans / subscriptions: trial settings shipped in P8-4; plans still P8-5.  
- Landing prices still hardcoded (P8-8).  
- Manual test guide still mentions signup `verification_token` in places (refresh at P8-10 docs gate).  
- Master login is not written to tenant `audit_logs`.

---

**Stopped.** Next: P8-5 Plan management — only after approval.
