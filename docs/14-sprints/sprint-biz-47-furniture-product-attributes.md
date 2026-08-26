# Sprint BIZ-47 – Furniture Product Attributes

## Objective

Dimensions, material, color on furniture items.

## Business Type

Furniture Shops

## Why This Sprint Is Required

Furniture special product data.

## Existing Functionality

Items.

## Missing Functionality

attribute fields.

## Scope

### Backend Tasks

- Attributes

### Frontend Tasks

- Furniture item form

### Database Tasks

- attributes

### API Tasks

- item payload

### UI/UX Tasks

- Form sections

### Testing Tasks

- Validation

### Documentation Tasks

- 10-furniture

## Database Changes

Conceptual entities only (no SQL in this plan):

- item attributes

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- items

## Frontend Pages

- FurnitureItems

## User Roles

Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Catalog.

## Notifications

None.

## Acceptance Criteria

- Attributes stored/shown

## Dependencies

BIZ-10

## Risks

- None

## Definition of Done

- Attributes done

## Status

COMPLETED

## Deliverables

- Module `furniture_attributes` on `furniture` business type
- Columns on `items`: `dimension_length` / `width` / `height`, `material`, `color`
- Migration: `20260826_biz47_furniture_product_attributes`
- Search `q` matches material/color; Items UI gated form + list
- Tests: `test_biz47_furniture_product_attributes.py` (5 passed)

## Phase

Phase 09 – Furniture
