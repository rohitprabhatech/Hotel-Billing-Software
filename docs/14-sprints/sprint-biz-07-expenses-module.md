# Sprint BIZ-07 – Expenses Module

## Objective

Track business expenses for P&L style reporting later.

## Business Type

All (common core)

## Why This Sprint Is Required

Listed as core for restaurants, bakery, furniture, wholesale, travel.

## Existing Functionality

None.

## Missing Functionality

expenses entity + UI + basic report.

## Scope

### Backend Tasks

- Expense CRUD
- Category optional

### Frontend Tasks

- Expenses pages

### Database Tasks

- expenses

### API Tasks

- CRUD /expenses

### UI/UX Tasks

- Simple form

### Testing Tasks

- Isolation
- date filters

### Documentation Tasks

- 11-expenses

## Database Changes

Conceptual entities only (no SQL in this plan):

- expenses (tenant_id, category, amount, date, notes)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- CRUD /expenses

## Frontend Pages

- /owner/expenses

## User Roles

Owner/Manager; Billing User no.

## Tenant Isolation

Standard tenant scoping.

## Audit Requirements

Expense mutations.

## Notifications

None.

## Acceptance Criteria

- CRUD + list filters

## Dependencies

BIZ-04

## Risks

- Chart of accounts creep — keep simple categories

## Definition of Done

- Usable for daily expense entry

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
