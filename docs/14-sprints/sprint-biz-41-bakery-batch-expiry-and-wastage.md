# Sprint BIZ-41 – Bakery Batch Expiry and Wastage

## Objective

Batches/expiry for finished goods; wastage.

## Business Type

Bakery / Sweet Shops

## Why This Sprint Is Required

Perishable goods.

## Existing Functionality

Grocery batches BIZ-22; F&B wastage BIZ-18.

## Missing Functionality

Bakery defaults/enablement.

## Scope

### Backend Tasks

- Enable batch for bakery items

### Frontend Tasks

- Bakery batch UI

### Database Tasks

- Reuse item_batches, wastage

### API Tasks

- Reuse

### UI/UX Tasks

- Same

### Testing Tasks

- Expiry

### Documentation Tasks

- bakery batch

## Database Changes

Conceptual entities only (no SQL in this plan):

- reuse

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- reuse

## Frontend Pages

- Batches

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Yes.

## Notifications

Expiring batches.

## Acceptance Criteria

- Batch sell rules

## Dependencies

BIZ-40, BIZ-22

## Risks

- None

## Definition of Done

- Enabled for bakery type

## Status

NOT STARTED

## Phase

Phase 07 – Bakery / Food Production
