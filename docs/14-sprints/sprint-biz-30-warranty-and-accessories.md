# Sprint BIZ-30 – Warranty and Accessories

## Objective

Warranty period on serial/sale; accessories as related items.

## Business Type

Mobile + Electronics

## Why This Sprint Is Required

Special for both verticals.

## Existing Functionality

None.

## Missing Functionality

warranty fields, accessory links.

## Scope

### Backend Tasks

- Warranty on serial_unit/bill_item
- Accessory relations

### Frontend Tasks

- Warranty display on invoice

### Database Tasks

- warranty fields

### API Tasks

- extend bill payload

### UI/UX Tasks

- Invoice section

### Testing Tasks

- Warranty dates

### Documentation Tasks

- warranty

## Database Changes

Conceptual entities only (no SQL in this plan):

- serial_units.warranty_months
- bill_items.warranty_until

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- sale payload

## Frontend Pages

- Invoice
- Item form

## User Roles

Owner sets defaults.

## Tenant Isolation

Standard.

## Audit Requirements

Warranty edits rare — audit if changed post-sale.

## Notifications

Warranty expiry later optional.

## Acceptance Criteria

- Invoice shows warranty

## Dependencies

BIZ-29

## Risks

- None

## Definition of Done

- Print/PDF includes warranty

## Status

NOT STARTED

## Phase

Phase 05 – Mobile / Electronics
