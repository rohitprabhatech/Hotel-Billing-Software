# Sprint BIZ-52 – Sales Orders and Purchase Orders

## Objective

SO/PO documents before billing/purchasing.

## Business Type

Wholesale Shops

## Why This Sprint Is Required

Wholesale workflow.

## Existing Functionality

Purchases; bills; quotations.

## Missing Functionality

sales_orders, purchase_orders.

## Scope

### Backend Tasks

- SO/PO services
- Convert SO→bill, PO→purchase

### Frontend Tasks

- SO/PO pages

### Database Tasks

- sales_orders
- purchase_orders
- line tables

### API Tasks

- /sales-orders
- /purchase-orders

### UI/UX Tasks

- Document UIs

### Testing Tasks

- Conversions

### Documentation Tasks

- SO/PO

## Database Changes

Conceptual entities only (no SQL in this plan):

- sales_orders
- purchase_orders

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- SO/PO

## Frontend Pages

- SalesOrders
- PurchaseOrders

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Document lifecycle.

## Notifications

None.

## Acceptance Criteria

- SO→Bill
- PO→Purchase

## Dependencies

BIZ-51, BIZ-06

## Risks

- Partial fulfillments — v1 full convert only

## Definition of Done

- Happy path

## Status

NOT STARTED

## Phase

Phase 10 – Wholesale
