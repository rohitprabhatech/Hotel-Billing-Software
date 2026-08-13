# 17 — Security

## Principles

1. Authenticate every protected request
2. Authorize by role
3. Isolate by tenant from JWT/server context
4. Validate all inputs
5. Never trust frontend money or `tenant_id`
6. Minimize secret exposure
7. Preserve auditability of sensitive actions

## Controls

### Authentication

- JWT with strong secret from environment
- Password hashing (bcrypt/argon2)
- Inactive user / suspended tenant cannot login
- Rate limit login attempts

### Authorization

- Role allow-lists per endpoint
- Owner-only: users, reports, audit, tenant settings mutations
- Billing User limited to billing operations + active catalog read

### Tenant Isolation

- Derive `tenant_id` from token/user record only
- All queries include tenant predicate
- Resource access by `(id, tenant_id)`
- Automated isolation tests mandatory

### Data Protection

- No hard delete of bills, bill_items, sales aggregates, audit logs via app
- Soft cancel/void and deactivate patterns
- `password_hash` never in API responses
- Internal exceptions not returned to clients

### Transport & CORS

- HTTPS in production
- CORS allowlist of frontend origins

### Secrets Management

Store in env / secret manager:

```text
SECRET_KEY
JWT_SECRET_KEY
DATABASE_URL
```

Never commit `.env` or hard-code secrets.

### Input Validation

- Schema validation on bodies/queries
- Max lengths on strings
- Decimal bounds on money and quantities
- Mandatory cancellation reason

### SQL Injection

- SQLAlchemy ORM / bound parameters only
- No raw string-interpolated SQL

### XSS / Frontend

- React escaping by default
- Avoid `dangerouslySetInnerHTML` for user content
- Careful token storage

### Audit

- Log security-relevant and business-sensitive actions
- Owner-visible investigation trail

## Explicit Non-Exposures

Do not expose to frontend:

- password_hash
- JWT secret
- database password
- stack traces / internal exception details

## Threat Scenarios

| Threat | Mitigation |
|--------|------------|
| Cross-tenant IDOR | Tenant filter + 404 |
| Privilege escalation | Role guards |
| Totals manipulation | Server recalculation |
| Bill deletion fraud | No delete; cancel + audit |
| Brute force login | Rate limit |
| Replay of cancelled bill as active | Status checks |

## Production Checklist

- [ ] Strong secrets rotated
- [ ] DEBUG off
- [ ] HTTPS
- [ ] CORS locked
- [ ] DB user least privilege
- [ ] Backups enabled
- [ ] Migration process controlled
