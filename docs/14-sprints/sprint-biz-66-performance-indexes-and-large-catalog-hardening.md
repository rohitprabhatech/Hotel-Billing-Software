# Sprint BIZ-66 – Performance Indexes and Large Catalog Hardening

## Objective

Ensure industry modules do not slow common billing; pagination/indexes/lazy nav.

## Business Type

All

## Why This Sprint Is Required

Performance requirement.

## Existing Functionality

Some indexes; master pagination patterns.

## Missing Functionality

Barcode/serial/warehouse indexes; POS query budgets.

## Scope

### Backend Tasks

- Query review
- Indexes via migrations when coding approved

### Frontend Tasks

- Virtualized lists where needed

### Database Tasks

- Index plan documented

### API Tasks

- Pagination enforced

### UI/UX Tasks

- Lazy load module routes

### Testing Tasks

- Load tests light

### Documentation Tasks

- perf

## Database Changes

Conceptual entities only (no SQL in this plan):

- indexes

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- list endpoints

## Frontend Pages

- POS, items

## User Roles

N/A.

## Tenant Isolation

Indexed with tenant_id leading.

## Audit Requirements

N/A.

## Notifications

N/A.

## Acceptance Criteria

- POS search p95 budget documented+met on staging

## Dependencies

BIZ-65

## Risks

- Premature indexes — measure first

## Definition of Done

- Perf report

## Status

NOT STARTED

## Phase

Phase 13 – Security / Testing / Performance
