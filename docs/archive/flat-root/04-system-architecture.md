# 04 — System Architecture

## High-Level Architecture

```text
┌─────────────────┐     HTTPS/JSON      ┌──────────────────────────┐
│  React + MUI    │ ◄─────────────────► │  Flask REST API (/api/v1) │
│  Frontend SPA   │      JWT Bearer     │  Controllers → Services   │
└─────────────────┘                     │  → Repositories → Models  │
                                        └────────────┬─────────────┘
                                                     │ SQLAlchemy
                                                     ▼
                                        ┌──────────────────────────┐
                                        │  MySQL (shared schema)   │
                                        │  tenant_id isolation     │
                                        └──────────────────────────┘
```

## Components

### Frontend (SPA)

- React Router for auth, owner, and billing route trees
- Axios client with JWT interceptor
- Auth context holding user role + profile (not tenant_id for authorization decisions on server)
- Role-based layouts: Owner layout vs Billing layout
- Printable receipt route/component isolated from dashboard chrome

### Backend (API)

| Layer | Responsibility |
|-------|----------------|
| Routes | URL mapping, HTTP methods |
| Controllers | Parse request, call services, return response envelopes |
| Services | Business rules, calculations, orchestration, audit |
| Repositories | Tenant-scoped data access |
| Models | SQLAlchemy ORM entities |
| Schemas | Validation / serialization |
| Middleware | JWT auth, role checks, error handlers, rate limit |

### Database

- Single MySQL database, shared schema
- Row-level isolation via `tenant_id`
- Migrations via Flask-Migrate (Alembic)

## Request Flow (Authenticated)

```text
Client Request + JWT
        ↓
Auth Middleware → validate JWT → load user_id, role, tenant_id
        ↓
Role Guard → allow/deny endpoint
        ↓
Controller → Schema validation
        ↓
Service → business logic (e.g., recalculate bill)
        ↓
Repository → queries ALWAYS filtered by tenant_id from JWT context
        ↓
Response Envelope { success, data, error, meta }
```

## Critical Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Multi-tenancy model | Shared DB + `tenant_id` | Simpler ops for SaaS v1; strict query discipline |
| Money | `DECIMAL` + Python `Decimal` | Avoid float rounding errors |
| Bill mutations | Status workflow | Preserve financial history |
| Totals authority | Backend only | Never trust React totals |
| Tenant source | JWT claims / server user record | Never trust frontend `tenant_id` |
| Roles | Exactly two | Matches product scope |

## Runtime Context Object

After authentication, request context includes:

```text
current_user_id
current_tenant_id
current_role          # OWNER | BILLING_USER
ip_address
user_agent
```

Services and repositories consume this context; controllers do not accept `tenant_id` from body/query for isolation.

## Cross-Cutting Concerns

- **Audit**: Service layer writes audit rows in the same transaction where appropriate
- **Errors**: Centralized handlers map exceptions to HTTP status + safe messages
- **CORS**: Allow configured frontend origins only
- **Config**: Environment-based (`DATABASE_URL`, `JWT_SECRET`, etc.)

## Related Documents

- [05-multi-tenant-architecture.md](./05-multi-tenant-architecture.md)
- [15-frontend-architecture.md](./15-frontend-architecture.md)
- [16-backend-architecture.md](./16-backend-architecture.md)
