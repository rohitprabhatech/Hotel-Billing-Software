# Sprint BIZ-27 – Clothing Exchange and Return

## Objective

Return/exchange flows restocking variants and linking original bill.

## Business Type

Clothing Shops

## Why This Sprint Is Required

Clothing special.

## Existing Functionality

Bill cancel only.

## Missing Functionality

returns/exchanges.

## Scope

### Backend Tasks

- Return service
- Stock in
- Optional exchange bill

### Frontend Tasks

- Return wizard

### Database Tasks

- returns
- return_items

### API Tasks

- /returns

### UI/UX Tasks

- Wizard steps

### Testing Tasks

- Stock restore
- Audit

### Documentation Tasks

- returns

## Database Changes

Conceptual entities only (no SQL in this plan):

- sales_returns

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- returns

## Frontend Pages

- Returns

## User Roles

Owner/Manager; Billing limited.

## Tenant Isolation

Standard.

## Audit Requirements

Returns with old/new stock.

## Notifications

None.

## Acceptance Criteria

- Return restocks correct variant

## Dependencies

BIZ-26

## Risks

- Partial returns GST — keep simple

## Definition of Done

- Return E2E

## Status

NOT STARTED

## Phase

Phase 04 – Clothing
