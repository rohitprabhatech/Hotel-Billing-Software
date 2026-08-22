# SaaS Hotel Registration & Auth Enhancement

## Goal

Enable self-serve multi-hotel onboarding while preserving existing billing, printing, reports, and JWT-bound tenant isolation.

## Architecture decisions

| Topic | Decision |
|-------|----------|
| Tenant ID | UUID generated server-side only; never accepted from client for scoping |
| Tenant context | JWT → DB user validation → `RequestContext.tenant_id` |
| Email uniqueness | App-level global uniqueness for login email (new registrations) |
| Email verification | Required when `EMAIL_VERIFICATION_REQUIRED=true` |
| Password reset | Hashed single-use tokens with expiry |
| Session revoke | `token_version` in JWT; bumped on password change |
| Hotel profile | Existing `GET/PUT /tenants/me` (extended, not replaced) |
| Email transport | SMTP via env; suppress + outbox in tests/dev |

## New / extended APIs

```
POST /api/v1/auth/register-hotel
POST /api/v1/auth/verify-email
POST /api/v1/auth/resend-verification
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
POST /api/v1/auth/change-password
GET  /api/v1/profile
PUT  /api/v1/profile
POST /api/v1/profile/request-email-change
```

Existing `GET/PUT /tenants/me` remains the hotel information API.

## Schema additions

- `users.email_verified`, `email_verified_at`, `password_changed_at`, `pending_email`, `token_version`
- `password_reset_tokens`
- `email_verification_tokens`

## Implementation order

1. Migrations + models
2. Email service
3. Auth registration / verify / password flows
4. Profile APIs
5. Frontend pages + layout polish
6. Tests
