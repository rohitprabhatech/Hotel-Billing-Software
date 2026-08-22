# Sprint BIZ-29 – Shared Serial / IMEI Unit Stock

## Objective

Serialized inventory units (IMEI/serial) unique per tenant; sell specific unit.

## Business Type

Mobile Shops + Electronics (shared)

## Why This Sprint Is Required

Mobile and electronics share serial tracking.

## Existing Functionality

Qty stock only.

## Missing Functionality

serial_units.

## Scope

### Backend Tasks

- Unit registry
- Allocate on bill
- Prevent duplicate IMEI

### Frontend Tasks

- IMEI receive
- POS IMEI capture

### Database Tasks

- serial_units

### API Tasks

- /serial-units

### UI/UX Tasks

- Scan/type IMEI

### Testing Tasks

- Duplicate blocked
- Sold unit not resellable

### Documentation Tasks

- shared serial module

## Database Changes

Conceptual entities only (no SQL in this plan):

- serial_units (tenant_id, item_id, serial, status)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- serial APIs

## Frontend Pages

- SerialStock
- POS

## User Roles

Owner receive; Billing sell.

## Tenant Isolation

Unique (tenant_id, serial).

## Audit Requirements

Unit status transitions.

## Notifications

None.

## Acceptance Criteria

- IMEI-wise stock list
- Bill binds serial

## Dependencies

BIZ-10

## Risks

- Qty vs serial dual modes on item — flag track_serial

## Definition of Done

- Shared module for both verticals

## Status

NOT STARTED

## Phase

Phase 05 – Mobile / Electronics
