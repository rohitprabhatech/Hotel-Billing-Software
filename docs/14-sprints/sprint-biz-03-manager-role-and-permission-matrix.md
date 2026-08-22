# Sprint BIZ-03 – Manager Role and Permission Matrix

## Objective

Add Manager role between Owner and Billing User with documented permissions.

## Business Type

All (platform)

## Why This Sprint Is Required

Docs require Manager; code only has OWNER and BILLING_USER.

## Existing Functionality

OWNER, BILLING_USER; user CRUD for owners.

## Missing Functionality

MANAGER role; permission checks for stock edits, cancels, reports, industry ops.

## Scope

### Backend Tasks

- Seed MANAGER role
- Permission helpers
- Enforce on sensitive routes

### Frontend Tasks

- Role selector on Users page
- Hide forbidden actions

### Database Tasks

- roles row; no schema break if roles table already flexible

### API Tasks

- User create/update accepts MANAGER

### UI/UX Tasks

- Consistent users table

### Testing Tasks

- Manager cannot access Master
- Permission matrix cases

### Documentation Tasks

- Update roles requirements

## Database Changes

Conceptual entities only (no SQL in this plan):

- roles
- users.role_id

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- POST/PATCH /users

## Frontend Pages

- Owner Users

## User Roles

Owner: full tenant admin. Manager: ops + reports (configurable). Billing User: billing POS + limited catalog read.

## Tenant Isolation

Users belong to one tenant; role cannot escalate to Master.

## Audit Requirements

User create/role change audited.

## Notifications

Optional: notify owner when manager created.

## Acceptance Criteria

- MANAGER creatable
- Matrix enforced API+UI
- No cross-tenant user assign

## Dependencies

BIZ-02 (optional soft dep) or BIZ-01

## Risks

- Too-permissive manager — start restrictive

## Definition of Done

- Matrix doc + tests pass

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
