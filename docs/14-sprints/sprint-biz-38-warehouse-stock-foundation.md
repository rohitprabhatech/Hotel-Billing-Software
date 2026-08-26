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

COMPLETED

## Phase

Phase 06 – Hardware / Building Material

## Implementation notes (2026-08-25)

- Tables: `warehouses`, `warehouse_stocks`, `stock_transfers` (+ lines/counter); `bills.warehouse_id`
- Default warehouse `MAIN` auto-created; seeds from `items.stock_quantity`
- Transfers conserve item total; bill can sell from selected warehouse
- Purchases receive into default warehouse when module on
- APIs: `/api/v1/warehouses`, `/warehouses/stocks`, `/stock-transfers`
- UI: Owner Warehouses page (locations / balances / transfers)
- Alembic: `20260825_biz38_warehouse_stock_foundation`
- Tests: `test_biz38_warehouse_stock_foundation.py`

### Default warehouse migration plan

1. On first warehouse API use (or list), ensure one default `MAIN` per tenant with `warehouse` module.
2. Copy each tracked `items.stock_quantity` into `warehouse_stocks` for MAIN (idempotent if rows already exist for that warehouse).
3. Keep `items.stock_quantity` as billing aggregate; warehouse balances must sum to it for transferred stock (transfers do not change item total).
4. Alembic creates empty tables; runtime seed handles existing tenants without a separate data migration script.
