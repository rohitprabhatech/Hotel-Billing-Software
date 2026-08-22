# Phase 2 Sprint P2-3 — Auth / registration verification

**Date:** 2026-08-14  
**Goal:** Prove Register Business + login + verify + password flows against current APIs.  
**Scope:** Verification only; fix regressions if found.  
**Result:** **PASS** — no application code changes required.

---

## Automated tests

Command (project venv):

```text
python -m pytest tests/test_auth.py tests/test_saas_registration_auth.py -q
```

| Suite | Result |
|-------|--------|
| `tests/test_auth.py` | ✅ Pass |
| `tests/test_saas_registration_auth.py` | ✅ Pass |
| **Total** | **16 passed** |

Covered: login (owner/billing), `/me`, role guards, logout, register → verify → login, `business_type` persistence + label, legacy `/auth/register-hotel`, duplicate email 409, forgot/reset password, change-password revokes token, tenant isolation by type.

---

## Live API smoke (local `run.py` + MySQL)

Base: `http://127.0.0.1:5000/api/v1`

| Check | Expected | Result |
|-------|----------|--------|
| `GET /health` | 200 | ✅ |
| `GET /tenants/business-types` | list of types | ✅ 9 types |
| `POST /auth/register-business` (`grocery_store`) | 201 + `business_type` | ✅ |
| `POST /auth/login` before verify | 401 | ✅ |
| `POST /auth/verify-email` | 200 | ✅ |
| `POST /auth/login` after verify | OWNER + `grocery_store` | ✅ |
| `GET /auth/me` / `GET /tenants/me` | same tenant + type | ✅ |
| `POST /auth/register-hotel` (legacy) | 201 + type | ✅ `restaurant` |
| Invalid `business_type` | 400 | ✅ |
| Password mismatch on register | 400 | ✅ (schema) |
| `POST /auth/forgot-password` + `reset-password` | 200 + login with new pwd | ✅ |

---

## Frontend wiring review

| Surface | Status |
|---------|--------|
| `/register` → `RegisterBusinessPage` → `POST /auth/register-business` | ✅ |
| Business type select from `GET /tenants/business-types` | ✅ |
| FSSAI shown only when type is FSSAI-relevant | ✅ |
| Dev verify redirect when `verification_token` returned | ✅ |
| `/login`, `/verify-email`, `/forgot-password`, `/reset-password?token=` | ✅ wired |
| `RegisterHotelPage.jsx` re-exports Register Business | ✅ (compat) |
| API legacy `/auth/register-hotel` | ✅ (no separate FE route needed) |

---

## Notes / non-blockers

- Live DB seed users may differ from pytest fixtures; smoke used a fresh register + reset path.
- Change-password rejects “new password same as current” with 400 — expected validation, not a regression.
- No payment gateway / email provider required for these checks when `ALLOW_DEV_AUTH_TOKENS` exposes tokens in API responses.

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Smoke register / login / reset | ✅ |
| `business_type` persistence | ✅ |
| Legacy `register-hotel` alias safe | ✅ |
| Documented pass/fail | ✅ (this file) |
| Fixes only if regressions | ✅ N/A — none found |
