# Sprint BIZ-56 – Travel Tour Package Management

## Objective

Tour packages with pricing (service-oriented, not classic SKU stock).

## Business Type

Travel Agencies

## Why This Sprint Is Required

Travel is service-first; packages replace product stock.

## Existing Functionality

Items could model packages poorly; expenses; customers; bills.

## Missing Functionality

tour_packages entity.

## Scope

### Backend Tasks

- Package CRUD
- Optional inventory=false

### Frontend Tasks

- Package catalog

### Database Tasks

- tour_packages

### API Tasks

- /tour-packages

### UI/UX Tasks

- Package cards still use design system (interaction containers OK)

### Testing Tasks

- No stock deduct for packages

### Documentation Tasks

- 14-travel

## Database Changes

Conceptual entities only (no SQL in this plan):

- tour_packages

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- tour-packages

## Frontend Pages

- Packages

## User Roles

Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Package changes.

## Notifications

None.

## Acceptance Criteria

- Packages billable without negative stock

## Dependencies

BIZ-10, BIZ-04

## Risks

- Forcing travel into item stock model — avoid

## Definition of Done

- Service billing path clear

## Status

NOT STARTED

## Phase

Phase 11 – Travel Agency
