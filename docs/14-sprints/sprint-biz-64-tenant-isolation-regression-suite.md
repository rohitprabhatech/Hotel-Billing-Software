# Sprint BIZ-64 – Tenant Isolation Regression Suite

## Objective

Automated isolation tests across all new entities.

## Business Type

All

## Why This Sprint Is Required

Hard rule: no tenant_id manipulation.

## Existing Functionality

Some isolation tests.

## Missing Functionality

Coverage for every new table/API.

## Scope

### Backend Tasks

- Parametrized isolation tests

### Frontend Tasks

- N/A

### Database Tasks

- Fixtures two tenants

### API Tasks

- Negative IDOR tests

### UI/UX Tasks

- N/A

### Testing Tasks

- This sprint focus

### Documentation Tasks

- security testing

## Database Changes

Conceptual entities only (no SQL in this plan):

- All tenant-owned

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- All industry

## Frontend Pages

- N/A

## User Roles

Attacker as Billing User of tenant A.

## Tenant Isolation

Primary focus.

## Audit Requirements

Verify audit still tenant scoped.

## Notifications

N/A.

## Acceptance Criteria

- Zero cross-tenant reads in suite

## Dependencies

BIZ-63

## Risks

- Flaky fixtures

## Definition of Done

- Suite in CI

## Status

NOT STARTED

## Phase

Phase 13 – Security / Testing / Performance
