# Sprint BIZ-61 – Cross-Business Reports Enhancement

## Objective

Unify industry report hooks into common Reports hub without slowing core queries.

## Business Type

All

## Why This Sprint Is Required

Avoid 14 isolated report apps.

## Existing Functionality

ReportsPage + APIs.

## Missing Functionality

Module-aware report registry, pagination guarantees.

## Scope

### Backend Tasks

- Report registry
- Index review

### Frontend Tasks

- Dynamic report list by modules

### Database Tasks

- Indexes only as needed

### API Tasks

- /reports/available

### UI/UX Tasks

- Same reports shell

### Testing Tasks

- Large date range performance budget

### Documentation Tasks

- reporting

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- reports

## Frontend Pages

- Reports

## User Roles

Owner/Manager.

## Tenant Isolation

Yes.

## Audit Requirements

N/A.

## Notifications

N/A.

## Acceptance Criteria

- Only enabled module reports show
- Perf budget met

## Dependencies

BIZ-19,BIZ-24,BIZ-28,BIZ-34,BIZ-39,BIZ-43,BIZ-46,BIZ-50,BIZ-55,BIZ-60

## Risks

- Report explosion — registry discipline

## Definition of Done

- Registry live

## Status

COMPLETED

## Phase

Phase 12 – Cross-Business Reports / AI / Notifications
