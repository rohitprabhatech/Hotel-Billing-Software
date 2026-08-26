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
- `GET /notifications/templates`

### UI/UX Tasks

- Same bell

### Testing Tasks

- Emit on events

### Documentation Tasks

- notifications

## Database Changes

None (in-code registry; optional DB table deferred).

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

- `GET /api/v1/notifications/templates` — module-filtered catalog
- Existing list/mark-read endpoints unchanged

## Frontend Pages

- N/A (NotificationBell reuses existing feed)

## User Roles

Owner, Manager, Billing user (same as notifications).

## Tenant Isolation

Yes — catalog filtered by tenant modules; emits scoped by `tenant_id`.

## Audit Requirements

N/A.

## Notifications

This sprint.

## Acceptance Criteria

- At least 5 industry events notify
- Templates listed in docs
- Rate limit / dedupe reduces spam

## Dependencies

BIZ-62

## Risks

- Notification spam — rate limit

## Definition of Done

- Templates listed in docs

## Status

COMPLETED

## Phase

Phase 12 – Cross-Business Reports / AI / Notifications
