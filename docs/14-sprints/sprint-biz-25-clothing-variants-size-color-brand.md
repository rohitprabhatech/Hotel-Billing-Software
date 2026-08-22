# Sprint BIZ-25 – Clothing Variants – Size Color Brand

## Objective

Variant model for size/color/brand; SKU per variant.

## Business Type

Clothing Shops

## Why This Sprint Is Required

Clothing special stock is variant-wise.

## Existing Functionality

Single item stock.

## Missing Functionality

variants.

## Scope

### Backend Tasks

- Variant entity
- Bill lines reference variant

### Frontend Tasks

- Variant matrix UI

### Database Tasks

- item_variants

### API Tasks

- /items/:id/variants

### UI/UX Tasks

- Matrix editor

### Testing Tasks

- Unique size+color per item

### Documentation Tasks

- 04-clothing

## Database Changes

Conceptual entities only (no SQL in this plan):

- item_variants (size, color, brand, barcode, stock)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- variants CRUD

## Frontend Pages

- VariantManager

## User Roles

Owner catalog.

## Tenant Isolation

Standard.

## Audit Requirements

Variant changes.

## Notifications

Low variant stock.

## Acceptance Criteria

- Size/color stock independent

## Dependencies

BIZ-10, BIZ-08

## Risks

- Migrating existing items — default single variant

## Definition of Done

- Variants sellable

## Status

NOT STARTED

## Phase

Phase 04 – Clothing
