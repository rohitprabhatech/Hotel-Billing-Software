# Sprint BIZ-42 – Custom Cake Orders and Advance Payments

## Objective

Custom cake orders with size/flavor, advance/remaining, delivery datetime, status.

## Business Type

Bakery / Sweet Shops

## Why This Sprint Is Required

Bakery special orders.

## Existing Functionality

Customers; bills; furniture-like advances later similar.

## Missing Functionality

custom_orders for bakery.

## Scope

### Backend Tasks

- Custom order service
- Advance ledger/payment

### Frontend Tasks

- Order form + status board

### Database Tasks

- custom_product_orders

### API Tasks

- /custom-orders

### UI/UX Tasks

- Status pipeline

### Testing Tasks

- Advance < total
- Status transitions

### Documentation Tasks

- cake orders

## Database Changes

Conceptual entities only (no SQL in this plan):

- custom_product_orders

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- custom-orders

## Frontend Pages

- CakeOrders

## User Roles

Billing creates; Owner manages.

## Tenant Isolation

Standard.

## Audit Requirements

Order+payment.

## Notifications

Delivery reminder.

## Acceptance Criteria

- Advance payment tracked
- Status board

## Dependencies

BIZ-41, BIZ-04

## Risks

- Overlap with furniture custom orders — share generic custom_order type

## Definition of Done

- Prefer shared custom_order entity with type=bakery

## Status

COMPLETED

## Deliverables

- Shared `custom_product_orders` + `custom_order_payments` (`order_type=bakery`, `CO-#####`)
- API: `/api/v1/custom-orders` (+ `/bakery/cake-orders` aliases)
- Advances must be < total on create; additional advances up to remaining
- Status board: BOOKED → CONFIRMED → IN_PRODUCTION → READY → DELIVERED
- Billing creates / records advance; Owner/Manager manage status
- Notifications: delivery scheduled, order ready
- UI: Owner Cake Orders page
- Migration: `20260825_biz42_custom_product_orders`
- Tests: `test_biz42_custom_cake_orders.py` (5 passed)

## Phase

Phase 07 – Bakery / Food Production
