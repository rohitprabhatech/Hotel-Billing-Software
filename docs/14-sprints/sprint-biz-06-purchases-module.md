# Sprint BIZ-06 – Purchases Module

## Objective

Record purchases that increase stock with supplier linkage and movement ledger.

## Business Type

All (common core)

## Why This Sprint Is Required

Required by most retail/wholesale verticals; currently only ad-hoc receive-stock.

## Existing Functionality

receive-stock + stock_movements.

## Missing Functionality

purchase headers/lines, returns later optional.

## Scope

### Backend Tasks

- Purchase create → stock increase + StockMovement
- List/filter

### Frontend Tasks

- Purchase list/create

### Database Tasks

- purchases
- purchase_items

### API Tasks

- POST/GET /purchases

### UI/UX Tasks

- Form with line items

### Testing Tasks

- Stock increases correctly
- Cannot over-receive negative

### Documentation Tasks

- 09-purchases

## Database Changes

Conceptual entities only (no SQL in this plan):

- purchases
- purchase_items

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- POST /purchases
- GET /purchases
- GET /purchases/:id

## Frontend Pages

- /owner/purchases

## User Roles

Owner/Manager create; Billing User typically no.

## Tenant Isolation

Purchase scoped to tenant; items must belong to same tenant.

## Audit Requirements

Purchase create/cancel audited.

## Notifications

Optional low-stock clear when restocked.

## Acceptance Criteria

- Purchase updates stock atomically
- Ledger row written

## Dependencies

BIZ-05

## Risks

- Concurrency with billing deductions — use row locks like bill_service

## Definition of Done

- Parity with existing stock lock patterns

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
