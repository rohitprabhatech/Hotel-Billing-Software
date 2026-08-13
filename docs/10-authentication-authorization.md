# 10 — Authentication & Authorization

## Authentication

### Mechanism

- JWT access tokens (Bearer)
- Password hashing (bcrypt or argon2)
- Login updates `users.last_login_at`
- Audit events: `LOGIN`, `LOGOUT`

### Login Flow

```text
Client credentials
    → validate email/password for user
    → ensure user.is_active and tenant.status == ACTIVE
    → issue JWT with sub, tenant_id, role, exp
    → return token + safe user profile
```

### Password Rules (v1)

- Minimum length enforced (e.g., 8+)
- Never return `password_hash` in any response
- Owner can reset Billing User password

### Token Handling

- Frontend stores token in memory and/or `httpOnly` cookie strategy; if localStorage used, document XSS risks and mitigate
- Axios attaches `Authorization` header
- Expired token → 401 → redirect to login

## Authorization

### Layers

1. **Authentication** — valid JWT required
2. **Role guard** — OWNER vs BILLING_USER endpoint allow-list
3. **Tenant scope** — repository filters by JWT `tenant_id`
4. **Resource ownership** — `(id, tenant_id)` lookups

### Middleware Pseudo-Flow

```text
extract Bearer token
verify signature & expiry
load user (optional freshness check)
attach RequestContext(user_id, tenant_id, role, ip, ua)
if endpoint requires OWNER and role != OWNER → 403
```

### Role Decorator Examples

```text
@auth_required
@roles_required("OWNER")
def list_audit_logs(...): ...

@auth_required
@roles_required("OWNER", "BILLING_USER")
def create_bill(...): ...
```

## Tenant Binding

```text
JWT.tenant_id  ==  users.tenant_id  (must match)
```

All writes set `tenant_id` from context, not from payload.

## Authorization Failure Responses

| Case | Status | Body |
|------|--------|------|
| Missing/invalid token | 401 | `UNAUTHORIZED` |
| Valid user, wrong role | 403 | `FORBIDDEN` |
| Resource not in tenant | 404 | `NOT_FOUND` (prefer no cross-tenant existence leak) |

## Session / Logout

v1: client discards JWT. Optional server-side token denylist can be added later.

## Rate Limiting

Apply stricter limits to:

- `POST /auth/login`
- password reset endpoints

## Provisioning

Initial OWNER for a tenant created via secure seed/onboarding (not by Billing User). Billing Users created only by OWNER within same tenant.
