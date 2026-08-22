# Sprint BIZ-51 – Wholesale Pricing Matrices

## Objective

Wholesale vs retail vs customer-wise pricing.

## Business Type

Wholesale Shops

## Why This Sprint Is Required

Core wholesale differentiator.

## Existing Functionality

Price tiers BIZ-21; customers.

## Missing Functionality

price lists / customer price assignments.

## Scope

### Backend Tasks

- Price list engine

### Frontend Tasks

- Price list admin
- POS price resolution

### Database Tasks

- price_lists
- customer_price_lists

### API Tasks

- price-lists

### UI/UX Tasks

- Admin tables

### Testing Tasks

- Resolution order

### Documentation Tasks

- 13-wholesale

## Database Changes

Conceptual entities only (no SQL in this plan):

- price_lists
- price_list_items
- customer_price_lists

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /price-lists

## Frontend Pages

- PriceLists

## User Roles

Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Price list changes.

## Notifications

None.

## Acceptance Criteria

- Customer-specific price applies

## Dependencies

BIZ-10, BIZ-21, BIZ-04

## Risks

- Complex resolution — document priority

## Definition of Done

- Resolver documented+tested

## Status

NOT STARTED

## Phase

Phase 10 – Wholesale
