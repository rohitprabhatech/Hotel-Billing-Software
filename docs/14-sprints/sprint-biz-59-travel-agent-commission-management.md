# Sprint BIZ-59 – Travel Agent Commission Management

## Objective

Agent records and commission on bookings.

## Business Type

Travel Agencies

## Why This Sprint Is Required

Travel special.

## Existing Functionality

None.

## Missing Functionality

agents, commissions.

## Scope

### Backend Tasks

- Agent CRUD
- Commission calc

### Frontend Tasks

- Agents + commission report

### Database Tasks

- travel_agents
- commission_entries

### API Tasks

- /travel-agents
- /commissions

### UI/UX Tasks

- Report table

### Testing Tasks

- Commission math

### Documentation Tasks

- commission

## Database Changes

Conceptual entities only (no SQL in this plan):

- travel_agents
- commission_entries

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- agents/commissions

## Frontend Pages

- Agents

## User Roles

Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Commission entries.

## Notifications

None.

## Acceptance Criteria

- Commission report by agent

## Dependencies

BIZ-58

## Risks

- None

## Definition of Done

- Commission E2E

## Status

COMPLETED

## Phase

Phase 11 – Travel Agency
