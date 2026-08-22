# Sprint BIZ-67 – Industry Modules Migration and Ops Runbook

## Objective

Document Alembic migration order, feature flag rollout, rollback; never full 02_schema.sql on live.

## Business Type

All

## Why This Sprint Is Required

Safe production enablement.

## Existing Functionality

Alembic Phase 8 head.

## Missing Functionality

Industry migration runbook.

## Scope

### Backend Tasks

- Migration plan docs only until approved

### Frontend Tasks

- N/A

### Database Tasks

- Ordered migration list

### API Tasks

- N/A

### UI/UX Tasks

- N/A

### Testing Tasks

- Migration dry-run on staging

### Documentation Tasks

- runbook

## Database Changes

Conceptual entities only (no SQL in this plan):

- all new

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- N/A

## Frontend Pages

- N/A

## User Roles

Ops/Master.

## Tenant Isolation

N/A.

## Audit Requirements

Platform audit for flag flips.

## Notifications

N/A.

## Acceptance Criteria

- Runbook reviewed

## Dependencies

BIZ-66

## Risks

- Big-bang enable — prefer per-type flags

## Definition of Done

- Runbook in docs/

## Status

NOT STARTED

## Phase

Phase 14 – Production Readiness
