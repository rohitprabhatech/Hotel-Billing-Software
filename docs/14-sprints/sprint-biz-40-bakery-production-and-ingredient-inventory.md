# Sprint BIZ-40 – Bakery Production and Ingredient Inventory

## Objective

Production runs consuming ingredients (reuse recipe patterns) producing finished goods stock.

## Business Type

Bakery / Sweet Shops

## Why This Sprint Is Required

Bakery special production.

## Existing Functionality

Recipe patterns from BIZ-16; stock movements.

## Missing Functionality

production_runs.

## Scope

### Backend Tasks

- Production service

### Frontend Tasks

- Production entry

### Database Tasks

- production_runs
- production_run_items

### API Tasks

- /productions

### UI/UX Tasks

- Simple production form

### Testing Tasks

- Ingredient down, FG up

### Documentation Tasks

- 07-bakery

## Database Changes

Conceptual entities only (no SQL in this plan):

- production_runs

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- productions

## Frontend Pages

- Production

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Production audited.

## Notifications

Low ingredients.

## Acceptance Criteria

- Production stock effects correct

## Dependencies

BIZ-16, BIZ-10

## Risks

- Tight coupling to restaurant recipes — share carefully

## Definition of Done

- Production E2E

## Status

NOT STARTED

## Phase

Phase 07 – Bakery / Food Production
