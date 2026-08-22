# System Architecture

```
PRABHA BILLING SaaS
  ├── Master Platform (plans, trial, approvals, audit)
  ├── Common Core (billing, inventory, customers, payments, reports, …)
  └── Industry Modules (14 packs)
```

Request path: Frontend → API → AuthN → AuthZ → Tenant resolution → Service → DB → Response.

See also backend/frontend/api docs in this folder. Full narrative: migrated from prior `architecture.md`.
