# Sprint BIZ-53 – Wholesale Multi-Warehouse and Stock Transfer

## Objective

Enable warehouse module fully for wholesale.

## Business Type

Wholesale Shops

## Why This Sprint Is Required

Multiple warehouses required.

## Existing Functionality

BIZ-38 foundation.

## Missing Functionality

Wholesale defaults + transfer UX polish.

## Scope

### Backend Tasks

- Enable
- Transfer validations

### Frontend Tasks

- Wholesale warehouse UI

### Database Tasks

- Reuse

### API Tasks

- Reuse

### UI/UX Tasks

- Same

### Testing Tasks

- Multi-warehouse sales

### Documentation Tasks

- warehouse wholesale

## Database Changes

Conceptual entities only (no SQL in this plan):

- Reuse

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- Reuse

## Frontend Pages

- Warehouses

## User Roles

Owner/Manager.

## Tenant Isolation

Yes.

## Audit Requirements

Transfers.

## Notifications

Low per WH.

## Acceptance Criteria

- Sell from selected warehouse

## Dependencies

BIZ-38, BIZ-52

## Risks

- None

## Definition of Done

- Wholesale warehouse E2E

## Status

NOT STARTED

## Phase

Phase 10 – Wholesale
