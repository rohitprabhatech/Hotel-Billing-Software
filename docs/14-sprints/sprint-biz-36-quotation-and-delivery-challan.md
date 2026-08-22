# Sprint BIZ-36 – Quotation and Delivery Challan

## Objective

Quotations and delivery challans convertible to bills.

## Business Type

Hardware + Building Material (+ Wholesale reuse)

## Why This Sprint Is Required

Building material & wholesale need these docs.

## Existing Functionality

Bills/PDF only.

## Missing Functionality

quotes, challans.

## Scope

### Backend Tasks

- Quote/Challan services
- Convert to bill

### Frontend Tasks

- Quote builder
- Challan print

### Database Tasks

- quotations
- delivery_challans

### API Tasks

- /quotations
- /challans

### UI/UX Tasks

- Document print layouts

### Testing Tasks

- Convert preserves lines

### Documentation Tasks

- shared documents

## Database Changes

Conceptual entities only (no SQL in this plan):

- quotations
- quotation_items
- delivery_challans

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- quotes/challans

## Frontend Pages

- Quotations
- Challans

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Document lifecycle.

## Notifications

None.

## Acceptance Criteria

- Quote→Bill
- Challan PDF

## Dependencies

BIZ-35

## Risks

- Document numbering per tenant

## Definition of Done

- Reusable for wholesale

## Status

NOT STARTED

## Phase

Phase 06 – Hardware / Building Material
