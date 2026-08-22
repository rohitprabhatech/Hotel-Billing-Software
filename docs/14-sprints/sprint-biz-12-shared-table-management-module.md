# Sprint BIZ-12 – Shared Table Management Module

## Objective

Reusable dining table entity with status Available / Occupied / Reserved; merge support design.

## Business Type

Hotels / Restaurants + Cafes / Tea Shops (shared)

## Why This Sprint Is Required

Both Restaurant and Cafe need tables — one module.

## Existing Functionality

bills.table_number free text only.

## Missing Functionality

tables entity, floor/section optional, status machine, merge.

## Scope

### Backend Tasks

- Table CRUD
- Status transitions
- Merge tables API

### Frontend Tasks

- Floor/table board
- Status colors

### Database Tasks

- dining_tables
- table_sessions optional

### API Tasks

- CRUD /tables
- POST /tables/:id/status
- POST /tables/merge

### UI/UX Tasks

- Board view responsive; touch-friendly

### Testing Tasks

- Invalid status transitions
- Isolation

### Documentation Tasks

- Shared module note

## Database Changes

Conceptual entities only (no SQL in this plan):

- dining_tables (tenant_id, code, capacity, status, section)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /api/v1/tables*

## Frontend Pages

- /owner/tables or /billing/tables

## User Roles

Manager/Billing update status; Owner configures tables.

## Tenant Isolation

Tables never cross tenants.

## Audit Requirements

Status changes + merge audited.

## Notifications

Optional reserved reminder.

## Acceptance Criteria

- Statuses work
- Cafe+Restaurant can enable same module

## Dependencies

BIZ-11

## Risks

- Realtime kitchen sync later — start with polling

## Definition of Done

- Shared module flagged for cafe too

## Status

COMPLETED (2026-08-22)

## Deliverables

- `dining_tables` entity with code, section, capacity, status, merge linkage
- CRUD + status transitions + merge/unmerge APIs
- Permissions: `tables.read`, `tables.write`, `tables.status`
- Frontend: responsive table board with status colors and 30s polling
- Migration: `20260822_biz12_dining_tables`
- Tests: `backend/tests/test_biz12_table_management.py`

## Phase

Phase 02 – Restaurant / Cafe
