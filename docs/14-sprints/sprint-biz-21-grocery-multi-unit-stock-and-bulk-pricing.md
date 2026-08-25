# Sprint BIZ-21 – Grocery Multi-Unit Stock and Bulk Pricing

## Objective

Sell in kg/g/l/pcs with bulk price breaks.

## Business Type

Grocery / Kirana

## Why This Sprint Is Required

Special grocery requirement.

## Existing Functionality

UoM foundation BIZ-08; single price on item.

## Missing Functionality

price tiers by qty.

## Scope

### Backend Tasks

- Price tier engine

### Frontend Tasks

- Tier editor
- POS applies tier

### Database Tasks

- item_price_tiers

### API Tasks

- tiers CRUD

### UI/UX Tasks

- Tier table

### Testing Tasks

- Tier boundaries

### Documentation Tasks

- bulk pricing

## Database Changes

Conceptual entities only (no SQL in this plan):

- item_price_tiers

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /items/:id/price-tiers

## Frontend Pages

- Item pricing

## User Roles

Owner sets tiers.

## Tenant Isolation

Standard.

## Audit Requirements

Tier changes.

## Notifications

None.

## Acceptance Criteria

- POS price matches tier

## Dependencies

BIZ-20

## Risks

- Rounding

## Definition of Done

- Tiers work

## Status

COMPLETED

## Phase

Phase 03 – Grocery / Retail
