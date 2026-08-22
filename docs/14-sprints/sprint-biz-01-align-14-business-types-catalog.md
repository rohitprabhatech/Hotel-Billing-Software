# Sprint BIZ-01 – Align 14 Business Types Catalog

## Objective

Replace the live 9-code business type catalog with the approved 14 types; keep Medical Store excluded.

## Business Type

All (platform)

## Why This Sprint Is Required

Code still uses restaurant/hotel/kirana/… while docs require 14 industry packs. Registration and module flags depend on a single catalog.

## Existing Functionality

`business_types.py` with 9 codes; registration/settings pickers; FSSAI hint for restaurant/hotel.

## Missing Functionality

14 codes (`hotel_restaurant`, `cafe_tea`, `grocery_kirana`, `clothing`, `mobile`, `hardware`, `bakery_sweet`, `stationery`, `electronics`, `furniture`, `building_material`, `book_store`, `wholesale`, `travel_agency`); migration mapping from old codes; no Medical.

## Scope

### Backend Tasks

- Update constants/catalog API
- Safe migrate/map existing tenant business_type values
- Registration validation for new codes

### Frontend Tasks

- Update Register + Settings pickers
- Update dashboard labels

### Database Tasks

- No new tables; tenants.business_type value domain change + data mapping

### API Tasks

- GET /tenants/business-types returns 14 types
- Registration accepts new codes only

### UI/UX Tasks

- Same design system; label copy only

### Testing Tasks

- Enum validation tests
- Migration mapping tests
- Medical code rejected

### Documentation Tasks

- Update supported-business-types if codes change
- Note mapping table

## Database Changes

Conceptual entities only (no SQL in this plan):

- tenants.business_type (domain update)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- GET /api/v1/tenants/business-types
- PATCH tenant profile business_type

## Frontend Pages

- RegisterBusinessPage
- Owner Settings

## User Roles

Master Admin: sees type on businesses. Owner: selects type at register/settings. Billing User: read-only label.

## Tenant Isolation

business_type is tenant attribute; cannot change another tenant's type.

## Audit Requirements

Log business_type changes (old→new) on tenant profile.

## Notifications

None required.

## Acceptance Criteria

- Exactly 14 selectable types
- No medical/pharmacy option
- Existing tenants mapped without data loss

## Dependencies

None (first business-development sprint). Platform baseline already in production.

## Risks

- Breaking old API clients expecting old codes — provide mapping

## Definition of Done

- Catalog live in staging
- Tests green
- Docs updated
- Status → COMPLETED only after approval+implementation

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
