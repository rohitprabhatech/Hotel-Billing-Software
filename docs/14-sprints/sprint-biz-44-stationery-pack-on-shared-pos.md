# Sprint BIZ-44 – Stationery Pack on Shared POS

## Objective

Enable stationery module using barcode POS, bulk pricing, credit, low-stock.

## Business Type

Stationery Shops

## Why This Sprint Is Required

Mostly configuration + light UX on shared modules.

## Existing Functionality

BIZ-08,21,09,20 patterns.

## Missing Functionality

Stationery defaults/nav.

## Scope

### Backend Tasks

- Module flags

### Frontend Tasks

- Stationery POS shortcuts

### Database Tasks

- Minimal

### API Tasks

- Reuse

### UI/UX Tasks

- Search-first POS

### Testing Tasks

- Flag + POS

### Documentation Tasks

- 08-stationery

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- Reuse

## Frontend Pages

- StationeryPOS

## User Roles

Billing.

## Tenant Isolation

Standard.

## Audit Requirements

Bills.

## Notifications

Low stock.

## Acceptance Criteria

- Stationery checklist without new heavy schema

## Dependencies

BIZ-24

## Risks

- Overbuilding — keep thin

## Definition of Done

- Pack enabled

## Status

COMPLETED

## Deliverables

- Modules on `stationery`: `barcode_pos`, `bulk_pricing`, `customer_credit` (no new migration)
- API aliases: `GET /api/v1/stationery/pos-catalog`, `/products/search`, `/products/by-barcode/<code>` (reuse grocery barcode POS)
- UI: `StationeryPosPage` — search-first POS + credit checkout at `/owner/stationery` and `/billing/stationery`
- Nav: Stationery POS shown only for `business_type=stationery`; Grocery POS hidden for stationery
- Tests: `test_biz44_stationery_pack.py` (4 passed)

## Phase

Phase 08 – Stationery / Books
