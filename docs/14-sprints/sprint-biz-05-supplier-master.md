# Sprint BIZ-05 – Supplier Master

## Objective

Tenant-scoped suppliers for purchase flows.

## Business Type

All (common core)

## Why This Sprint Is Required

Grocery, clothing, hardware, wholesale, etc. require suppliers; receive-stock is not enough.

## Existing Functionality

Receive stock with optional cost; no supplier entity.

## Missing Functionality

suppliers CRUD.

## Scope

### Backend Tasks

- Supplier service

### Frontend Tasks

- Suppliers pages

### Database Tasks

- suppliers

### API Tasks

- CRUD /suppliers

### UI/UX Tasks

- Same patterns as customers

### Testing Tasks

- Isolation
- permissions

### Documentation Tasks

- 07-suppliers module doc

## Database Changes

Conceptual entities only (no SQL in this plan):

- suppliers (tenant_id, name, phone, gstin, status)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- CRUD /api/v1/suppliers

## Frontend Pages

- /owner/suppliers

## User Roles

Owner/Manager full; Billing User read-only or none.

## Tenant Isolation

tenant_id server-side only.

## Audit Requirements

Supplier mutations audited.

## Notifications

None.

## Acceptance Criteria

- CRUD + isolation

## Dependencies

BIZ-04

## Risks

- GSTIN validation locale — keep optional

## Definition of Done

- Suppliers ready for Purchases sprint

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
