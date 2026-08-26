# Sprint BIZ-33 – Electronics Pack – Installation

## Objective

Installation tracking linked to serial sales.

## Business Type

Electronics Shops

## Why This Sprint Is Required

Electronics special.

## Existing Functionality

Repair tickets.

## Missing Functionality

installation jobs.

## Scope

### Backend Tasks

- Installation orders

### Frontend Tasks

- Installation schedule UI

### Database Tasks

- installation_orders

### API Tasks

- /installations

### UI/UX Tasks

- Calendar-ish list

### Testing Tasks

- Link to bill/serial

### Documentation Tasks

- 09-electronics

## Database Changes

Conceptual entities only (no SQL in this plan):

- installation_orders

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- installations

## Frontend Pages

- Installations

## User Roles

Manager/Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Installation status.

## Notifications

Installation scheduled/done.

## Acceptance Criteria

- Installation statuses

## Dependencies

BIZ-32

## Risks

- None

## Definition of Done

- Electronics checklist

## Status

COMPLETED (2026-08-25 on `rs/feature/billingV3`)

## Phase

Phase 05 – Mobile / Electronics
