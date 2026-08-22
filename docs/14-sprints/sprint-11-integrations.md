# Sprint 11 – Integrations

## Objective

WhatsApp, email, webhooks

## Why This Sprint Is Required

Establishes the next dependency in the approved roadmap. Coding begins only after documentation approval.

## Prerequisites

Sprint 10

## Scope

In scope: work listed under Tasks for this sprint.  
Out of scope: Medical Store features; unrelated phases.

## Tasks

### Backend

- Document then (post-approval) implement services for this sprint's scope.

### Frontend

- Document then (post-approval) implement UI for this sprint's scope.

### Database

- Schema/design notes only until coding is approved. Prefer Alembic migrations later — never full `02_schema.sql` on live.

### API

- Align with [../07-api/](../07-api/).

### UI/UX

- Align with [../08-ui-ux/](../08-ui-ux/).

### Testing

- Define cases under Test Cases; execute in Sprint 12+ gates as applicable.

### Documentation

- Keep this file and [sprint-tracker.md](./sprint-tracker.md) updated.

## Database Changes

TBD after documentation approval (design already in `03-database/`).

## API Changes

TBD after documentation approval.

## Frontend Changes

TBD after documentation approval.

## Security Requirements

Tenant isolation; no cross-tenant access; Master Admin separation; audit where applicable.

## Test Cases

- TEST-INT-001: Happy path for sprint objective
- TEST-INT-002: Negative / unauthorized access
- TEST-INT-003: Regression on prior phases

## Acceptance Criteria

- Objective met without Medical Store scope
- Tracker status updated
- No broken doc links for this sprint

## Dependencies

Sprint 10

## Definition of Done

- Tasks complete or explicitly deferred with reason
- Tests listed above pass (when coding starts)
- Docs updated

## Files/Modules Expected to Change

Documented after coding approval. Historical implementation notes live under `docs/archive/`.

## Risks

Scope creep into other phases; duplicate docs; accidental Medical Store requirements.

## Estimated Effort

TBD during planning workshop.

## Status

NOT STARTED
