# Sprint BIZ-10 – Common Platform Readiness Testing Gate

## Objective

Regression gate proving CRM/procurement/config/roles before industry packs.

## Business Type

All

## Why This Sprint Is Required

Do not start Restaurant until common gaps are stable.

## Existing Functionality

Pytest suite for bills/stock/master.

## Missing Functionality

Tests for new common modules + isolation matrix.

## Scope

### Backend Tasks

- Expand pytest coverage

### Frontend Tasks

- Manual checklist

### Database Tasks

- Verify migrations applied on staging only after approval

### API Tasks

- Contract tests

### UI/UX Tasks

- Responsive smoke

### Testing Tasks

- Functional, API, DB, tenant isolation, permissions, stock+purchase interaction

### Documentation Tasks

- Gate report template

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- N/A

## Frontend Pages

- N/A

## User Roles

QA + Owner scenarios.

## Tenant Isolation

Cross-tenant negative tests mandatory.

## Audit Requirements

Verify audit rows for new modules.

## Notifications

Smoke notifications still work.

## Acceptance Criteria

- Gate checklist 100% or waived with written risk

## Dependencies

BIZ-01 … BIZ-09

## Risks

- Scope slip into industry features

## Definition of Done

- Written gate sign-off doc in docs/14-sprints/

## Status

COMPLETED

## Gate artifacts

- Automated: `backend/tests/test_biz10_platform_readiness_gate.py`
- Sign-off: [biz-10-platform-readiness-gate-report.md](./biz-10-platform-readiness-gate-report.md)
- Manual UI: [biz-10-manual-frontend-checklist.md](./biz-10-manual-frontend-checklist.md)

## Phase

Phase 01 – Common Platform Readiness
