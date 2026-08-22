# Sprint BIZ-65 – Permission and Audit Completeness

## Objective

Ensure sensitive industry actions are permissioned and audited with old/new values.

## Business Type

All

## Why This Sprint Is Required

Owner must see add/edit/delete history.

## Existing Functionality

audit_logs.

## Missing Functionality

Coverage gaps on new modules.

## Scope

### Backend Tasks

- Audit wrappers
- Permission matrix update

### Frontend Tasks

- Audit filters by module

### Database Tasks

- N/A

### API Tasks

- audit list filters

### UI/UX Tasks

- AuditPage filters

### Testing Tasks

- Delete still leaves audit

### Documentation Tasks

- audit

## Database Changes

Conceptual entities only (no SQL in this plan):

- audit_logs

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /audit-logs

## Frontend Pages

- AuditPage

## User Roles

Owner views; users generate.

## Tenant Isolation

Yes.

## Audit Requirements

This sprint.

## Notifications

N/A.

## Acceptance Criteria

- Matrix + audit checklist 100%

## Dependencies

BIZ-64

## Risks

- PII in audit — redact secrets

## Definition of Done

- Checklist signed

## Status

NOT STARTED

## Phase

Phase 13 – Security / Testing / Performance
