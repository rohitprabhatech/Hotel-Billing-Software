# Sprint BIZ-63 – Module Notification Templates

## Objective

Notification templates for industry events (KOT ready, repair ready, booking due, expiry).

## Business Type

All

## Why This Sprint Is Required

Centralize notifications.

## Existing Functionality

Tenant notifications + low stock.

## Missing Functionality

Template keys per module.

## Scope

### Backend Tasks

- Template registry
- Emitters

### Frontend Tasks

- NotificationBell already

### Database Tasks

- Maybe template table optional

### API Tasks

- reuse notifications

### UI/UX Tasks

- Same bell

### Testing Tasks

- Emit on events

### Documentation Tasks

- notifications

## Database Changes

Conceptual entities only (no SQL in this plan):

- optional

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- notifications

## Frontend Pages

- N/A

## User Roles

All recipients per role.

## Tenant Isolation

Yes.

## Audit Requirements

N/A.

## Notifications

This sprint.

## Acceptance Criteria

- At least 5 industry events notify

## Dependencies

BIZ-62

## Risks

- Notification spam — rate limit

## Definition of Done

- Templates listed in docs

## Status

NOT STARTED

## Phase

Phase 12 – Cross-Business Reports / AI / Notifications
