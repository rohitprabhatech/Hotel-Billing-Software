# Sprint BIZ-57 – Travel Booking Management and Payments

## Objective

Bookings with status, advance/remaining payments linked to customers/packages.

## Business Type

Travel Agencies

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- Tables: `travel_bookings`, `travel_booking_payments`, `travel_booking_number_counters` (`TB-#####`)
- Migration: `20260826_biz57_travel_bookings`
- Status pipeline: BOOKED → CONFIRMED → IN_PROGRESS → COMPLETED (cancel allowed until complete)
- Complete blocked while remaining balance &gt; 0
- Notifications: `TRAVEL_BOOKING_CONFIRMED`, `TRAVEL_PAYMENT_DUE`
- APIs: `/travel-bookings` + `/travel/bookings` aliases

### Frontend

- `/owner/travel-bookings` status board + create + record payment

### Tests

- `backend/tests/test_biz57_travel_bookings.py` (4 passed)

## Acceptance Criteria

- [x] Advance + remaining
- [x] Status board

## Dependencies

BIZ-56

## Next

BIZ-58 — itinerary, hotel/vehicle/tickets, documents
