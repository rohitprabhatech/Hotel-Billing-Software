# Sprint BIZ-08 – Shared Barcode and Unit-of-Measure Foundations

## Objective

Extend items with barcode/SKU search and base UoM fields without industry-specific UI yet.

## Business Type

Reusable (Grocery, Stationery, Clothing, Hardware, Wholesale, Books)

## Why This Sprint Is Required

Multiple verticals need barcode + units; build once.

## Existing Functionality

items.sku, stock_quantity; bill item search by name/sku partial.

## Missing Functionality

Dedicated barcode field/index; uom (kg/g/l/pcs/m); conversion helpers.

## Scope

### Backend Tasks

- Item fields barcode, uom
- Lookup by barcode

### Frontend Tasks

- Item form fields
- POS barcode focus field (prep)

### Database Tasks

- items.barcode, items.uom (+ optional uom_conversions later)

### API Tasks

- GET /items?barcode=
- item payload fields

### UI/UX Tasks

- POS-friendly scan field styling

### Testing Tasks

- Unique barcode per tenant
- Lookup performance

### Documentation Tasks

- Inventory engine notes

## Database Changes

Conceptual entities only (no SQL in this plan):

- items columns; optional item_barcodes

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- GET /items/by-barcode/:code

## Frontend Pages

- ItemsPage
- NewBillPage scan

## User Roles

Owner manages catalog; Billing uses scan.

## Tenant Isolation

Barcode unique per tenant_id.

## Audit Requirements

Item field changes.

## Notifications

None.

## Acceptance Criteria

- Scan finds item
- UoM stored on item

## Dependencies

BIZ-02

## Risks

- Fractional qty billing — define decimal precision

## Definition of Done

- Shared foundation ready for grocery/hardware packs

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
