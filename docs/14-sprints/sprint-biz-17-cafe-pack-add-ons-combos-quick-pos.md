# Sprint BIZ-17 – Cafe Pack – Add-ons, Combos, Quick POS

## Objective

Cafe-specific overlays on shared table/KOT/order: add-ons, combos, quick billing defaults.

## Business Type

Cafes / Tea Shops

## Why This Sprint Is Required

Cafe shares modules but needs lighter UX and offers.

## Existing Functionality

Shared modules from BIZ-12–16; common billing.

## Missing Functionality

add-on groups, combo definitions, popular defaults.

## Scope

### Backend Tasks

- Add-on/combo models
- Price composition

### Frontend Tasks

- Quick cafe POS
- Add-on picker

### Database Tasks

- item_addons
- combo_items

### API Tasks

- addons/combos

### UI/UX Tasks

- Faster POS density; same design tokens

### Testing Tasks

- Combo stock rules

### Documentation Tasks

- 02-cafes-tea-shops

## Database Changes

Conceptual entities only (no SQL in this plan):

- item_addon_groups
- combo_definitions

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /menu/addons
- /combos

## Frontend Pages

- CafePOS

## User Roles

Billing primary; Owner configures offers.

## Tenant Isolation

Standard.

## Audit Requirements

Offer config changes.

## Notifications

None.

## Acceptance Criteria

- Cafe tenant enables cafe pack
- Restaurant unchanged

## Dependencies

BIZ-16

## Risks

- Pricing edge cases

## Definition of Done

- Cafe E2E order→bill

## Status

COMPLETED

## Phase

Phase 02 – Restaurant / Cafe
