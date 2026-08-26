# Sprint BIZ-58 – Travel Itinerary Hotel Vehicle Tickets Documents

## Objective

Capture itinerary, hotel/vehicle/ticket details, customer documents metadata.

## Business Type

Travel Agencies

## Why This Sprint Is Required

Travel special data.

## Existing Functionality

Bookings.

## Missing Functionality

related detail tables/files metadata.

## Scope

### Backend Tasks

- Child entities
- Document metadata (no medical)

### Frontend Tasks

- Tabs on booking detail

### Database Tasks

- travel_itinerary_items
- travel_booking_documents

### API Tasks

- nested resources

### UI/UX Tasks

- Tabbed detail

### Testing Tasks

- Cascade tenant checks

### Documentation Tasks

- itinerary

## Database Changes

Conceptual entities only (no SQL in this plan):

- itinerary + documents metadata

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- nested

## Frontend Pages

- BookingDetail

## User Roles

Owner/Manager.

## Tenant Isolation

Documents tenant-scoped.

## Audit Requirements

Document upload/delete.

## Notifications

None.

## Acceptance Criteria

- All detail sections save

## Dependencies

BIZ-57

## Risks

- PII in documents — encrypt at rest later note

## Definition of Done

- Detail complete

## Status

COMPLETED

## Phase

Phase 11 – Travel Agency
