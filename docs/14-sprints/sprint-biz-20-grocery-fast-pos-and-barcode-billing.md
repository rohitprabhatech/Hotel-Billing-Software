# Sprint BIZ-20 – Grocery Fast POS and Barcode Billing

## Objective

Enable grocery module; high-speed barcode POS on common billing.

## Business Type

Grocery / Kirana

## Why This Sprint Is Required

Kirana needs fast POS; reuse BIZ-08.

## Existing Functionality

NewBillPage; stock checks.

## Missing Functionality

Grocery UX defaults; qty decimals for weight.

## Scope

### Backend Tasks

- Grocery module flag
- Decimal qty support hardening

### Frontend Tasks

- Grocery POS layout

### Database Tasks

- Possibly none beyond BIZ-08

### API Tasks

- Barcode lookup

### UI/UX Tasks

- Keyboard/scan first

### Testing Tasks

- Rapid line add
- Stock block

### Documentation Tasks

- 03-grocery

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A new

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- existing bills + barcode

## Frontend Pages

- GroceryPOS

## User Roles

Billing User primary.

## Tenant Isolation

Standard.

## Audit Requirements

Bills audited as today.

## Notifications

Low stock.

## Acceptance Criteria

- Scan-to-bill under target UX

## Dependencies

BIZ-10, BIZ-08

## Risks

- Scale performance with large catalogs — index barcode

## Definition of Done

- POS usable

## Status

COMPLETED

## Phase

Phase 03 – Grocery / Retail
