# Sprint BIZ-22 – Grocery Expiry Tracking and Stock Adjustment

## Objective

Optional batch/expiry for grocery items; adjustments with reason.

## Business Type

Grocery / Kirana

## Why This Sprint Is Required

Expiry is grocery special; adjustments already partial via adjust-stock.

## Existing Functionality

adjust-stock + movements.

## Missing Functionality

batches/expiry dates.

## Scope

### Backend Tasks

- Batches
- FEFO optional

### Frontend Tasks

- Batch receive UI
- Expiry report

### Database Tasks

- item_batches

### API Tasks

- /batches

### UI/UX Tasks

- Date pickers

### Testing Tasks

- Expired batch not sellable if policy on

### Documentation Tasks

- expiry

## Database Changes

Conceptual entities only (no SQL in this plan):

- item_batches

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- batch APIs

## Frontend Pages

- Batches

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Adjustments + batch changes.

## Notifications

Expiring soon.

## Acceptance Criteria

- Expiry list
- Adjustment reasons required

## Dependencies

BIZ-21

## Risks

- Not all items need batches — keep optional

## Definition of Done

- Optional flag per item

## Status

COMPLETED

## Phase

Phase 03 – Grocery / Retail
