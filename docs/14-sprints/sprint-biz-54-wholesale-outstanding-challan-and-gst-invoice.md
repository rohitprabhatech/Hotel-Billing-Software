# Sprint BIZ-54 – Wholesale Outstanding Challan and GST Invoice

## Objective

Outstanding reports, challan, GST invoice using existing bill PDF + credit.

## Business Type

Wholesale Shops

## Why This Sprint Is Required

Wholesale special reporting docs.

## Existing Functionality

Reports, credit, challan, GST on bills.

## Missing Functionality

Outstanding aged report; wholesale invoice template tweaks.

## Scope

### Backend Tasks

- Aged outstanding report

### Frontend Tasks

- Outstanding + print

### Database Tasks

- N/A

### API Tasks

- /reports/outstanding

### UI/UX Tasks

- Report table

### Testing Tasks

- Aging buckets

### Documentation Tasks

- outstanding

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- reports

## Frontend Pages

- OutstandingReport

## User Roles

Owner/Manager.

## Tenant Isolation

Yes.

## Audit Requirements

N/A.

## Notifications

Optional dues.

## Acceptance Criteria

- Customer+supplier outstanding

## Dependencies

BIZ-53, BIZ-37

## Risks

- None

## Definition of Done

- Reports live

## Status

NOT STARTED

## Phase

Phase 10 – Wholesale
