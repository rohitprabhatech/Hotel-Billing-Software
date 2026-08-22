# Sprint BIZ-02 – Business Feature / Module Configuration Framework

## Objective

Introduce scalable feature flags per business type so industry modules enable without hard-coding UI/API everywhere.

## Business Type

All (platform)

## Why This Sprint Is Required

Architecture rule: COMMON + CONFIG + MODULES. Without flags, every screen will branch on business_type strings.

## Existing Functionality

Plan `features` JSON is marketing copy only; no module registry.

## Missing Functionality

Module registry; per-tenant or per-type feature map (table_management, kot, imei, variants, booking, …).

## Scope

### Backend Tasks

- Module catalog service
- Resolve enabled modules for current tenant
- Guard optional routes by module

### Frontend Tasks

- Nav/menu filter by enabled modules
- Feature gate hook

### Database Tasks

- Optional: business_type_modules, tenant_module_overrides — document entities

### API Tasks

- GET /me/modules or /tenants/me/features

### UI/UX Tasks

- Hide disabled nav items; no separate themes

### Testing Tasks

- Restaurant sees tables; clothing does not
- Cannot call disabled module API

### Documentation Tasks

- Module matrix in docs/00-project-foundation

## Database Changes

Conceptual entities only (no SQL in this plan):

- business_type_module_defaults
- tenant_module_overrides (optional)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- GET /api/v1/tenants/me/modules

## Frontend Pages

- Owner layout nav
- Billing layout nav

## User Roles

Owner/Manager see configured modules. Billing User sees subset. Master may view config.

## Tenant Isolation

Module resolution uses server tenant context only.

## Audit Requirements

Log module override changes if Master/Owner toggles.

## Notifications

None.

## Acceptance Criteria

- Default flags per 14 types
- Nav reflects flags
- Disabled APIs return 403/404 consistently

## Dependencies

BIZ-01

## Risks

- Over-flexible overrides confuse support — default by type first

## Definition of Done

- Framework merged
- Matrix documented
- Sample flags for Restaurant + Clothing verified

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness