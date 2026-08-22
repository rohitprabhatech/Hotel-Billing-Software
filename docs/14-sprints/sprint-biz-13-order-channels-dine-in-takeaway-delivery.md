# Sprint BIZ-13 – Order Channels – Dine-in / Takeaway / Delivery

## Objective

Order entity with channel type linking table session or takeaway/delivery metadata.

## Business Type

Hotels / Restaurants (+ Cafe)

## Why This Sprint Is Required

Workflow Table→Order requires structured orders before KOT.

## Existing Functionality

Direct bill create.

## Missing Functionality

orders, order_items, channel, link to table.

## Scope

### Backend Tasks

- Order service
- Convert order→bill later

### Frontend Tasks

- Order taking UI by channel

### Database Tasks

- orders
- order_items

### API Tasks

- CRUD orders
- add/remove lines

### UI/UX Tasks

- Channel selector

### Testing Tasks

- Dine-in requires table
- Takeaway does not

### Documentation Tasks

- Restaurant workflow

## Database Changes

Conceptual entities only (no SQL in this plan):

- orders
- order_items

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /orders

## Frontend Pages

- New Order

## User Roles

Billing/Manager create orders; Owner all.

## Tenant Isolation

Orders tenant-scoped.

## Audit Requirements

Order create/cancel.

## Notifications

None yet.

## Acceptance Criteria

- Three channels supported
- Table occupancy updates on dine-in

## Dependencies

BIZ-12

## Risks

- Duplicating bill lines — clear order→bill mapping

## Definition of Done

- Orders creatable without final payment

## Status

COMPLETED (2026-08-22)

## Deliverables

- `orders` + `order_items` with channels: `dine_in`, `takeaway`, `delivery`
- Dine-in links table and marks it occupied; cancel releases table
- CRUD lines, cancel, list/detail APIs (module: `order_channels`)
- `bill_id` reserved for order→bill conversion (BIZ-15)
- Frontend: Orders list + New Order page with channel selector
- Migration: `20260822_biz13_orders`
- Tests: `backend/tests/test_biz13_order_channels.py`

## Phase

Phase 02 – Restaurant / Cafe
