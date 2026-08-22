# 16 — Backend Architecture

## Stack

- Python / Flask
- Flask REST API
- SQLAlchemy
- Flask-Migrate
- MySQL
- JWT auth
- MVC + Service + Repository

## Folder Structure

```text
backend/
├── app/
│   ├── __init__.py              # App factory
│   ├── config/
│   │   └── settings.py
│   ├── extensions/
│   │   └── __init__.py          # db, migrate, jwt, limiter
│   ├── models/
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── category.py
│   │   ├── item.py
│   │   ├── bill.py
│   │   ├── bill_item.py
│   │   └── audit_log.py
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   ├── middleware/
│   ├── routes/
│   └── utils/                   # decimals, responses, timezones
├── migrations/
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

## Layer Responsibilities

| Layer | Does | Does Not |
|-------|------|----------|
| Routes | Map URLs | Business rules |
| Controllers | HTTP in/out, call services | Raw SQL / cross-tenant queries |
| Services | Rules, calculations, transactions, audit | Flask request parsing details |
| Repositories | Tenant-scoped CRUD/queries | Authorization policy beyond tenant filter |
| Models | ORM mapping | HTTP |
| Schemas | Validate/serialize | Persist |

## App Factory Pattern

```text
create_app(config)
  → init extensions
  → register error handlers
  → register blueprints under /api/v1
  → return app
```

## Response Helpers

Central helpers for success/error envelopes (see API docs).

## Transactions

Bill finalize / cancel / item critical updates:

```text
with db session transaction:
    mutate entities
    write audit_log
    commit
```

## Config

Environment variables:

```text
FLASK_ENV
SECRET_KEY
JWT_SECRET_KEY
DATABASE_URL
CORS_ORIGINS
JWT_ACCESS_TOKEN_EXPIRES
REPORT_TIMEZONE=Asia/Kolkata
```

## Error Handling

Map domain exceptions:

- `ValidationError` → 400
- `UnauthorizedError` → 401
- `ForbiddenError` → 403
- `NotFoundError` → 404
- `ConflictError` → 409

Log internals server-side; return safe client messages.

## Seed Data

- Roles: OWNER, BILLING_USER
- Optional demo tenant for local dev only
