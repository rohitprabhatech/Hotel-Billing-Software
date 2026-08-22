# Sprint BIZ-48 – Furniture Custom Orders and Payments

## Objective

Custom furniture orders with advance/remaining using shared custom_order.

## Business Type

Furniture Shops

## Why This Sprint Is Required

Special order workflow.

## Existing Functionality

Bakery custom_order pattern BIZ-42.

## Missing Functionality

Furniture type fields.

## Scope

### Backend Tasks

- Extend custom_order type=furniture

### Frontend Tasks

- Furniture order board

### Database Tasks

- Reuse custom_product_orders

### API Tasks

- Reuse

### UI/UX Tasks

- Pipeline

### Testing Tasks

- Payments

### Documentation Tasks

- furniture orders

## Database Changes

Conceptual entities only (no SQL in this plan):

- reuse

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- custom-orders

## Frontend Pages

- FurnitureOrders

## User Roles

Owner/Billing.

## Tenant Isolation

Standard.

## Audit Requirements

Orders+payments.

## Notifications

Delivery date.

## Acceptance Criteria

- Advance/remaining tracked

## Dependencies

BIZ-42, BIZ-47

## Risks

- None

## Definition of Done

- Shared entity used

## Status

NOT STARTED

## Phase

Phase 09 – Furniture
