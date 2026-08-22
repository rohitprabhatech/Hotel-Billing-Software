# Sprint BIZ-09 – Shared Party Ledger / Customer Credit Foundation

## Objective

Introduce credit/udhari ledger primitives linked to customers (and later suppliers).

## Business Type

Reusable (Grocery, Hardware, Stationery, Wholesale, Building Material)

## Why This Sprint Is Required

Credit appears in many verticals; avoid per-business ledgers.

## Existing Functionality

payment_method on bill; no outstanding balance.

## Missing Functionality

ledger entries, balance, partial payments against credit sales.

## Scope

### Backend Tasks

- Ledger service
- Credit sale path on bill
- Payment against balance

### Frontend Tasks

- Customer balance UI
- Collect payment dialog

### Database Tasks

- party_ledger_entries
- customers.balance cache optional

### API Tasks

- GET /customers/:id/ledger
- POST /customers/:id/payments

### UI/UX Tasks

- Balance badge on customer

### Testing Tasks

- No negative silent balances without rules
- Isolation

### Documentation Tasks

- Payments + credit

## Database Changes

Conceptual entities only (no SQL in this plan):

- party_ledger_entries (tenant_id, party_type, party_id, amount, ref_type, ref_id)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- ledger + payment endpoints

## Frontend Pages

- Customer detail
- Outstanding list

## User Roles

Owner/Manager manage credit; Billing User may record collection if allowed.

## Tenant Isolation

Ledger rows tenant-scoped; party must match tenant.

## Audit Requirements

Credit sale + collections audited.

## Notifications

Optional due reminders later (Phase 12).

## Acceptance Criteria

- Credit bill increases balance
- Payment decreases
- Report of outstanding

## Dependencies

BIZ-04

## Risks

- Accounting complexity — keep simple running balance

## Definition of Done

- Reusable API used by later grocery/wholesale sprints

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
