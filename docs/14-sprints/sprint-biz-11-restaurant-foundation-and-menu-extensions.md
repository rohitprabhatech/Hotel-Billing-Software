# Sprint BIZ-11 – Restaurant Foundation and Menu Extensions

## Objective

Enable restaurant module flag; menu/category conventions for F&B (courses, veg flag optional).

## Business Type

Hotels / Restaurants

## Why This Sprint Is Required

First industry pack foundation on top of common core.

## Existing Functionality

Items/categories/bills; business_type label; FSSAI print hint.

## Missing Functionality

Restaurant module enablement; menu metadata; order entity prelude.

## Scope

### Backend Tasks

- Enable modules for hotel_restaurant
- Optional item attributes (veg/is_menu)

### Frontend Tasks

- Restaurant home/dashboard widgets

### Database Tasks

- Optional item attribute JSON or columns

### API Tasks

- Module-aware menu list

### UI/UX Tasks

- Same shell; restaurant nav entries

### Testing Tasks

- Module flag on/off

### Documentation Tasks

- 05-businesses/01-hotels-restaurants

## Database Changes

Conceptual entities only (no SQL in this plan):

- item attributes; no tables yet

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- GET menu listing

## Frontend Pages

- Restaurant dashboard section

## User Roles

Owner configures menu; Billing/Manager take orders later.

## Tenant Isolation

Standard.

## Audit Requirements

Menu item changes.

## Notifications

None.

## Acceptance Criteria

- Restaurant tenant sees F&B nav
- Other types do not

## Dependencies

BIZ-10

## Risks

- Over-custom menu fields — keep minimal

## Definition of Done

- Foundation ready for tables sprint

## Status

COMPLETED (2026-08-22)

## Deliverables

- Module flag: `restaurant_menu` for `hotel_restaurant` and `cafe_tea`
- Item fields: `is_menu`, `is_veg` (optional)
- API: `GET /api/v1/menu` (module-gated, grouped by category/course)
- Frontend: Menu nav + page, item form toggles, owner dashboard widgets
- Migration: `20260822_biz11_restaurant_menu`
- Tests: `backend/tests/test_biz11_restaurant_foundation.py`

## Phase

Phase 02 – Restaurant / Cafe
