# Sprint BIZ-14 – KOT and Kitchen Dashboard

## Objective

Kitchen Order Tickets from orders; kitchen board statuses.

## Business Type

Hotels / Restaurants + Cafes

## Why This Sprint Is Required

Core F&B differentiator; shared Cafe/Restaurant.

## Existing Functionality

None.

## Missing Functionality

KOT print/view, kitchen status (queued/preparing/ready).

## Scope

### Backend Tasks

- KOT generation
- Status updates
- Idempotent reprints

### Frontend Tasks

- Kitchen dashboard
- KOT print view

### Database Tasks

- kots
- kot_items

### API Tasks

- POST /orders/:id/kot
- PATCH /kots/:id/status
- GET kitchen queue

### UI/UX Tasks

- Large touch targets; dark-mode friendly kitchen

### Testing Tasks

- KOT only for open orders
- Tenant isolation

### Documentation Tasks

- KOT workflow

## Database Changes

Conceptual entities only (no SQL in this plan):

- kots
- kot_items

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /kots*

## Frontend Pages

- KitchenDashboard

## User Roles

Kitchen/Manager update KOT; Billing fires KOT.

## Tenant Isolation

KOT scoped.

## Audit Requirements

KOT create/status.

## Notifications

Optional ready notify to waiter (later).

## Acceptance Criteria

- KOT appears on kitchen board
- Status flow works

## Dependencies

BIZ-13

## Risks

- Printer hardware variance — PDF/browser print first

## Definition of Done

- Cafe can reuse KOT module

## Status

COMPLETED

## Deliverables (implemented)

- **DB:** `kots`, `kot_items`, `kot_number_counters` — migration `20260822_biz14_kots.py`
- **API:** `POST /orders/:id/kot`, `GET /kots/kitchen/queue`, `PATCH /kots/:id/status`, `GET /kots/:id`
- **Permissions:** `kot.read`, `kot.write`, `kot.status`
- **Frontend:** Kitchen dashboard (dark board, 20s polling), Fire KOT from orders, print view at `/print/kots/:id`
- **Tests:** `test_biz14_kot_kitchen_dashboard.py`

## Phase

Phase 02 – Restaurant / Cafe
