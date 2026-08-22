# Sprint BIZ-37 – Trade Credit and Transport Charges

## Objective

Customer/supplier credit via shared ledger; transport charges on bills/challans.

## Business Type

Hardware + Building Material

## Why This Sprint Is Required

Special requirements.

## Existing Functionality

BIZ-09; suppliers; purchases.

## Missing Functionality

Transport charge field; supplier credit UX.

## Scope

### Backend Tasks

- Transport on bill
- Supplier ledger

### Frontend Tasks

- Fields + outstanding

### Database Tasks

- bill.transport_charge; supplier ledger via party_type

### API Tasks

- extend bill
- supplier ledger

### UI/UX Tasks

- Totals breakdown

### Testing Tasks

- Totals include transport

### Documentation Tasks

- credit+transport

## Database Changes

Conceptual entities only (no SQL in this plan):

- ledger party_type=supplier

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- ledger

## Frontend Pages

- Outstanding

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Credit + charge edits.

## Notifications

Optional dues.

## Acceptance Criteria

- Supplier+customer outstanding

## Dependencies

BIZ-09, BIZ-36

## Risks

- Double counting transport in GST — document tax treatment

## Definition of Done

- Checklist

## Status

NOT STARTED

## Phase

Phase 06 – Hardware / Building Material
