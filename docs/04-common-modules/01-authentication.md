# Authentication — Prabha Billing SaaS V2

## Actors

| Login | Path | Identity store |
|-------|------|----------------|
| Business Owner / Billing / Manager | `/login` | `users` |
| Master Admin | `/master/login` (footer dot) | `master_admins` |

Shared API: `POST /api/v1/auth/login` (current: tenant users then master).

## Behaviors

| Case | Expected |
|------|----------|
| Valid credentials | JWT + user payload |
| Invalid email/password | Generic error |
| Missing/invalid/expired token | 401 |
| Logout / password change | `token_version` bump → prior JWT invalid |
| Deactivated tenant | Login blocked |
| Inactive master | Login blocked |

## Tokens

- Access JWT with `role`, `tv`; Master **without** `tenant_id`.  
- Password hashes only; never return hashes.  
- Registration does **not** issue JWT until Master approve.

## Tests (architecture)

Valid/invalid login, token cases, logout, master vs owner path isolation — see [testing-guide.md](./testing-guide.md).
