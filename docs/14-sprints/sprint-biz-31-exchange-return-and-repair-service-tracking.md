# Sprint BIZ-31 – Exchange Return and Repair Service Tracking

## Objective

Exchange/return for serial goods; repair tickets.

## Business Type

Mobile + Electronics

## Why This Sprint Is Required

Special workflows.

## Existing Functionality

Cancel bill; clothing returns pattern may reuse.

## Missing Functionality

repair_orders; serial exchange.

## Scope

### Backend Tasks

- Repair ticket CRUD
- Serial return to stock/quarantine

### Frontend Tasks

- Repair board
- Exchange flow

### Database Tasks

- repair_orders

### API Tasks

- /repairs

### UI/UX Tasks

- Status board

### Testing Tasks

- Serial status after exchange

### Documentation Tasks

- repair

## Database Changes

Conceptual entities only (no SQL in this plan):

- repair_orders

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- repairs

## Frontend Pages

- Repairs

## User Roles

Manager/Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Repair status + exchanges.

## Notifications

Repair ready.

## Acceptance Criteria

- Repair statuses
- Exchange swaps serials

## Dependencies

BIZ-30, BIZ-27

## Risks

- Reuse returns module carefully

## Definition of Done

- E2E exchange+repair

## Status

NOT STARTED

## Phase

Phase 05 – Mobile / Electronics
