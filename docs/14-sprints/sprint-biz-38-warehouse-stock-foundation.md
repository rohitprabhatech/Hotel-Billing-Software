# Sprint BIZ-38 – Warehouse Stock Foundation

## Objective

Multi-location stock balances and transfers (foundation).

## Business Type

Building Material (+ Wholesale)

## Why This Sprint Is Required

Building material warehouses; wholesale needs same.

## Existing Functionality

Single stock_quantity on item.

## Missing Functionality

warehouses, warehouse_stocks, transfers.

## Scope

### Backend Tasks

- Warehouse CRUD
- Transfer service
- Bill warehouse selection

### Frontend Tasks

- Warehouse admin
- Transfer UI

### Database Tasks

- warehouses
- warehouse_stocks
- stock_transfers

### API Tasks

- /warehouses
- /stock-transfers

### UI/UX Tasks

- Location selectors

### Testing Tasks

- Transfer conserves qty
- Sell from correct warehouse

### Documentation Tasks

- warehouse

## Database Changes

Conceptual entities only (no SQL in this plan):

- warehouses
- warehouse_stocks
- stock_transfers

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- warehouse APIs

## Frontend Pages

- Warehouses

## User Roles

Owner/Manager.

## Tenant Isolation

Warehouses tenant-scoped.

## Audit Requirements

Transfers audited.

## Notifications

Low stock per warehouse.

## Acceptance Criteria

- Two warehouses transfer E2E

## Dependencies

BIZ-37

## Risks

- Migrating single stock → default warehouse

## Definition of Done

- Default warehouse migration plan documented

## Status

NOT STARTED

## Phase

Phase 06 – Hardware / Building Material
