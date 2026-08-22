# Sprint BIZ-23 – Grocery Credit and Reports

## Objective

Wire shared credit ledger into grocery POS; payment history; sales reports.

## Business Type

Grocery / Kirana

## Why This Sprint Is Required

Udhari is core kirana behavior.

## Existing Functionality

BIZ-09 ledger; reports.

## Missing Functionality

Grocery UX for credit sale + history.

## Scope

### Backend Tasks

- Integrate credit into bill create

### Frontend Tasks

- Credit toggle
- History

### Database Tasks

- Reuse ledger

### API Tasks

- Reuse

### UI/UX Tasks

- Clear credit indicators

### Testing Tasks

- Credit + stock

### Documentation Tasks

- grocery credit

## Database Changes

Conceptual entities only (no SQL in this plan):

- reuse

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- reuse

## Frontend Pages

- Customer outstanding

## User Roles

Owner/Billing as permitted.

## Tenant Isolation

Standard.

## Audit Requirements

Credit bills.

## Notifications

Optional dues.

## Acceptance Criteria

- Udhari flow E2E

## Dependencies

BIZ-09, BIZ-22

## Risks

- Cashier errors — confirm dialogs

## Definition of Done

- Kirana credit demoable

## Status

NOT STARTED

## Phase

Phase 03 – Grocery / Retail
