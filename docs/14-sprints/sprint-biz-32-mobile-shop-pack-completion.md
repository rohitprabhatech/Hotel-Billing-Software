# Sprint BIZ-32 – Mobile Shop Pack Completion

## Objective

Mobile-specific model/brand fields and purchase history UX.

## Business Type

Mobile Shops

## Why This Sprint Is Required

Pack polish on shared serial core.

## Existing Functionality

Shared serial/warranty/repair.

## Missing Functionality

Mobile model metadata UX.

## Scope

### Backend Tasks

- Attributes brand/model

### Frontend Tasks

- Mobile catalog fields

### Database Tasks

- item attributes

### API Tasks

- item fields

### UI/UX Tasks

- Mobile nav module

### Testing Tasks

- Mobile tenant flags

### Documentation Tasks

- 05-mobile

## Database Changes

Conceptual entities only (no SQL in this plan):

- attributes

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- items

## Frontend Pages

- Mobile catalog

## User Roles

Owner.

## Tenant Isolation

Standard.

## Audit Requirements

Catalog.

## Notifications

None.

## Acceptance Criteria

- Mobile module complete vs requirements checklist

## Dependencies

BIZ-31

## Risks

- None

## Definition of Done

- Checklist signed

## Status

NOT STARTED

## Phase

Phase 05 – Mobile / Electronics
