# Master Admin Security

# Security + Tenant Isolation Audit — Sprint 21

**Product:** Business Billing  
**Date:** 2026-08-14  
**Scope:** JWT, RBAC, tenant isolation / IDOR, password & token handling, route guards, audit immutability  

## Executive verdict

**Business A cannot access Business B** through the reviewed API paths. Repositories resolve entities with `tenant_id` from JWT/`RequestContext`; client-supplied `tenant_id` and bill money fields are not trusted.

No **Critical** IDOR was found. Sprint 21 hardened residual **High/Medium** session and identity risks (below).

---

## Findings (post-fix status)

| ID | Severity | Area | Finding | Status |
|----|----------|------|---------|--------|
| S21-01 | High | JWT logout | Logout audited only; JWT remained valid until expiry | **Fixed** — logout bumps `token_version` |
| S21-02 | High | Email identity | Billing-user create checked email only within tenant → cross-tenant duplicate emails / login ambiguity | **Fixed** — global email uniqueness on create/update |
| S21-03 | Medium | Password reset | Multiple unused reset tokens could remain valid | **Fixed** — prior unused tokens invalidated on issue/use |
| S21-04 | Medium | Email verify | Stacked unused verification tokens | **Fixed** — prior unused tokens invalidated per purpose |
| S21-05 | Medium | Deactivate user | Inactive user could keep using old JWT until expiry | **Fixed** — deactivate bumps `token_version` |
| S21-06 | Medium | Audit IP | Trusted client `X-Forwarded-For` by default | **Fixed** — only when `TRUST_PROXY_HEADERS=true` |
| S21-07 | Medium | JWT TTL | Default access token 24h | **Documented** — prefer 8–12h in production; logout now revokes |
| S21-08 | Medium | Audit DB | No UPDATE/DELETE API; DB triggers optional | **Accepted** — API immutable; DB defense-in-depth later |
| S21-09 | Low | Dev tokens | `ALLOW_DEV_AUTH_TOKENS` true in development | **Accepted** — forced false in production config |
| S21-10 | Info | Isolation / RBAC / bill totals / soft-delete | Already solid | **Confirmed** |

---

## Controls confirmed solid

1. **JWT validation** — Reloads user; checks active user/tenant, tenant/role match, `token_version`.  
2. **RBAC** — Owner-only: reports, AI, audit, users, `PUT /tenants/me`.  
3. **IDOR** — Bills, items, categories, users, audit, reports, AI scoped by tenant; cross-tenant GET → 404.  
4. **Bill create** — Server prices + GST; client `grand_total` / line `unit_price` ignored.  
5. **Passwords** — Hashed; reset/verify tokens stored hashed; password change revokes sessions.  
6. **Audit API** — Read-only; no update/delete routes.  
7. **Rate limiting** — Present on auth endpoints.  
8. **CORS** — Allowlist from env; production secret validation.

---

## Fixes shipped (code)

| Change | Location |
|--------|----------|
| Logout increments `token_version` | `auth_service.py` |
| Invalidate unused password-reset tokens | `auth_service.py` |
| Invalidate unused email-verification tokens | `auth_service.py` |
| Global email uniqueness for users | `user_service.py` |
| Deactivate bumps `token_version` | `user_service.py` |
| Proxy IP trust gated by env | `middleware/auth.py`, `settings.py`, `.env.example` |

---

## New automated tests

`backend/tests/test_security_hardening.py`:

- Logout revokes JWT  
- Deactivate user revokes JWT  
- Cannot create billing user with other tenant’s email  
- Bill rejects other-tenant `item_id`  
- Item GET other tenant → 404  
- Forgot-password invalidates previous reset tokens  
- Audit PUT/DELETE not allowed  
- Client `unit_price` / `grand_total` ignored  

Also covered previously: isolation suites for bills, categories, reports, AI, audit.

---

## Residual / follow-ups (non-blocking)

1. Optional **global unique DB index** on `users.email` (app-enforced now).  
2. Shorten production JWT TTL and/or add refresh tokens.  
3. DB triggers to block direct SQL mutation of `audit_logs`.  
4. Stronger password complexity policy (currently min length 8).  

---

## Acceptance

| Criterion | Result |
|-----------|--------|
| Prove Business A ↛ Business B | **Met** (design + tests) |
| JWT / RBAC / IDOR / password / audit | **Met** with Sprint 21 hardening |
| Written findings + critical fixes | **This document** + code fixes (no Critical open) |
