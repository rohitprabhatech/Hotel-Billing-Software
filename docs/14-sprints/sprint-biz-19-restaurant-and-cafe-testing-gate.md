# Sprint BIZ-19 – Restaurant and Cafe Testing Gate

## Objective

Full F&B test suite including workflow, stock, isolation, permissions.

## Business Type

Hotels / Restaurants + Cafes

## Why This Sprint Is Required

User requires dedicated business testing.

## Existing Functionality

Core pytest.

## Missing Functionality

F&B scenarios.

## Scope

### Backend Tasks

- API tests

### Frontend Tasks

- UI checklist

### Database Tasks

- Fixture tenants restaurant+cafe

### API Tasks

- Contract

### UI/UX Tasks

- Kitchen board on mobile

### Testing Tasks

- Functional, API, DB, isolation, permissions, stock, billing, reports, UI, regression

### Documentation Tasks

- Gate report

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- N/A

## Frontend Pages

- N/A

## User Roles

All F&B roles.

## Tenant Isolation

Two tenants cannot see tables/KOT.

## Audit Requirements

Spot-check.

## Notifications

Delivery still works on settled bills.

## Acceptance Criteria

- Gate signed

## Dependencies

BIZ-18

## Risks

- Flaky kitchen UI tests — prefer API-heavy

## Definition of Done

- Gate doc

## Status

COMPLETED

## Phase

Phase 02 – Restaurant / Cafe
