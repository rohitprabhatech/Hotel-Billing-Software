# Sprint BIZ-35 – Length Weight Area UoM Billing

## Objective

Bill by length/weight/area with decimal quantities (e.g., pipes).

## Business Type

Hardware Stores + Building Material

## Why This Sprint Is Required

Shared measurement selling.

## Existing Functionality

BIZ-08 UoM; grocery decimals.

## Missing Functionality

Area units; pricing per unit length.

## Scope

### Backend Tasks

- Measurement pricing helpers

### Frontend Tasks

- Qty unit labels on POS

### Database Tasks

- item measurement fields

### API Tasks

- price quote helper

### UI/UX Tasks

- Clear unit display

### Testing Tasks

- 10×450=4500 example

### Documentation Tasks

- 06-hardware

## Database Changes

Conceptual entities only (no SQL in this plan):

- items.sale_uom

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- quote

## Frontend Pages

- Hardware POS

## User Roles

Billing.

## Tenant Isolation

Standard.

## Audit Requirements

Bills.

## Notifications

Low stock.

## Acceptance Criteria

- Pipe example passes

## Dependencies

BIZ-10, BIZ-08

## Risks

- Floating point — use Decimal

## Definition of Done

- Shared by building material

## Status

COMPLETED

## Phase

Phase 06 – Hardware / Building Material

## Implementation notes (2026-08-25)

- `items.sale_uom` + area/length UoMs (`ft`, `sqm`, `sqft`); Decimal conversion via `app.utils.uom`
- Bill stock deduction converts sale qty → stock UoM
- APIs: `GET/POST /api/v1/hardware/units|pos-catalog|quote|convert` (module `uom_measurement`)
- Hardware POS UI (owner + billing); Items stock vs sale unit
- Tests: `backend/tests/test_biz35_length_weight_area_uom.py` (pipe 10×450=4500)
