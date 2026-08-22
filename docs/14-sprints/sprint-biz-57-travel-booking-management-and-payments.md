# Sprint BIZ-57 – Travel Booking Management and Payments

## Objective

Bookings with status, advance/remaining payments linked to customers/packages.

## Business Type

Travel Agencies

## Why This Sprint Is Required

Core travel workflow.

## Existing Functionality

Custom order payment patterns; customers.

## Missing Functionality

travel_bookings.

## Scope

### Backend Tasks

- Booking service
- Payment schedule

### Frontend Tasks

- Booking board

### Database Tasks

- travel_bookings
- travel_booking_payments

### API Tasks

- /travel-bookings

### UI/UX Tasks

- Pipeline statuses

### Testing Tasks

- Payment totals
- Status rules

### Documentation Tasks

- bookings

## Database Changes

Conceptual entities only (no SQL in this plan):

- travel_bookings
- travel_booking_payments

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- bookings

## Frontend Pages

- Bookings

## User Roles

Owner/Manager/Billing as configured.

## Tenant Isolation

Standard.

## Audit Requirements

Booking+payment.

## Notifications

Payment due / booking confirm.

## Acceptance Criteria

- Advance+remaining
- Status board

## Dependencies

BIZ-56

## Risks

- None

## Definition of Done

- Booking E2E

## Status

NOT STARTED

## Phase

Phase 11 – Travel Agency
