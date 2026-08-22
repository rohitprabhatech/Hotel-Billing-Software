# Sprint BIZ-18 – F&B Reports and Food Wastage

## Objective

Daily sales by channel/table; wastage logging against ingredients.

## Business Type

Hotels / Restaurants + Cafes

## Why This Sprint Is Required

Required special reports; wastage affects stock.

## Existing Functionality

Sales reports API/UI.

## Missing Functionality

Channel breakdown, wastage entries.

## Scope

### Backend Tasks

- Report extensions
- Wastage → stock movement

### Frontend Tasks

- F&B report tabs
- Wastage form

### Database Tasks

- wastage_entries

### API Tasks

- /reports/fb
- /wastage

### UI/UX Tasks

- Charts consistent with ReportsPage

### Testing Tasks

- Wastage deducts stock

### Documentation Tasks

- reports.md F&B

## Database Changes

Conceptual entities only (no SQL in this plan):

- wastage_entries

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- reports + wastage

## Frontend Pages

- FbReports
- Wastage

## User Roles

Owner/Manager.

## Tenant Isolation

Standard.

## Audit Requirements

Wastage audited.

## Notifications

None.

## Acceptance Criteria

- Channel sales report
- Wastage stock effect

## Dependencies

BIZ-17

## Risks

- Report performance — paginate/date bound

## Definition of Done

- Reports documented

## Status

COMPLETED

## Phase

Phase 02 – Restaurant / Cafe
