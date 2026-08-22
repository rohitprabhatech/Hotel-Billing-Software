# Sprint BIZ-49 – Furniture Delivery and Installation Tracking

## Objective

Delivery management + installation tracking for furniture orders.

## Business Type

Furniture Shops

## Why This Sprint Is Required

Special.

## Existing Functionality

Electronics installation; challans.

## Missing Functionality

Furniture delivery schedule UX.

## Scope

### Backend Tasks

- Delivery status on orders
- Reuse installation optionally

### Frontend Tasks

- Delivery board

### Database Tasks

- delivery fields

### API Tasks

- patch status

### UI/UX Tasks

- Board

### Testing Tasks

- Statuses

### Documentation Tasks

- delivery

## Database Changes

Conceptual entities only (no SQL in this plan):

- order delivery fields

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- orders

## Frontend Pages

- Deliveries

## User Roles

Manager/Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Status changes.

## Notifications

Out for delivery / delivered.

## Acceptance Criteria

- Delivery statuses

## Dependencies

BIZ-48, BIZ-33

## Risks

- None

## Definition of Done

- Board live

## Status

NOT STARTED

## Phase

Phase 09 – Furniture
