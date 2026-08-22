# Sprint BIZ-15 – Restaurant Billing – Split, Discount, Service Charge

## Objective

Settle orders to bills with split bill, discount, service charge; stock deduction rules.

## Business Type

Hotels / Restaurants

## Why This Sprint Is Required

Completes Table→…→Payment→Invoice path using existing bill engine.

## Existing Functionality

Bills with GST, stock validation, payments method, PDF/WA.

## Missing Functionality

Split/merge bill logic, service charge, order settlement.

## Scope

### Backend Tasks

- Settle order→bill(s)
- Split by items/amount
- Service charge calc

### Frontend Tasks

- Settlement UI
- Split dialog

### Database Tasks

- Maybe bill.service_charge; link order_id

### API Tasks

- POST /orders/:id/settle
- POST /bills/split

### UI/UX Tasks

- Consistent with NewBillPage

### Testing Tasks

- Stock deduct once
- Split totals = original

### Documentation Tasks

- Billing workflow F&B

## Database Changes

Conceptual entities only (no SQL in this plan):

- orders.bill_id
- bill extra fields

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- settle/split

## Frontend Pages

- Settlement

## User Roles

Billing/Manager settle; Owner void/cancel per policy.

## Tenant Isolation

Settlement within tenant.

## Audit Requirements

Settle, split, discount audited with amounts.

## Notifications

Reuse bill delivery.

## Acceptance Criteria

- Full workflow to paid bill
- No double stock deduct
- Insufficient stock blocked

## Dependencies

BIZ-14

## Risks

- Partial settle complexity

## Definition of Done

- E2E dine-in happy path

## Status

COMPLETED

## Deliverables (implemented)

- **DB:** `bills.order_id`, `bills.service_charge`, `bills.split_group_id` — migration `20260822_biz15_restaurant_billing.py`
- **API:** `POST /orders/:id/settle`, `POST /bills/split`
- **Backend:** `OrderSettlementService` — full/split settle, proportional discount & service charge, single stock deduct pass
- **Frontend:** `SettleOrderDialog` on Orders page (full bill + 2-way split), auto-print first bill
- **Tests:** `test_biz15_restaurant_billing.py`

## Phase

Phase 02 – Restaurant / Cafe
