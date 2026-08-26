# Travel Agencies — Database

> Conceptual only. No tables created in documentation phase.

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | Reused |
| Customer | COMMON ENTITY | Reused |
| Bill | COMMON ENTITY | Reused |
| BillItem | COMMON ENTITY | Reused |
| Payment | COMMON ENTITY | Reused |
| StockMovement | COMMON ENTITY | Reused |
| Notification | COMMON ENTITY | Reused |
| AuditLog | COMMON ENTITY | Reused |
| BusinessSettings | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC ENTITIES

| Entity | Class | Purpose |
|--------|-------|---------|
| TourPackage | BUSINESS-SPECIFIC | Sellable package/service (`tour_packages`; linked untracked `items` row) |
| TravelBooking | BUSINESS-SPECIFIC | Customer booking (`travel_bookings` / payments) |
| TravelItineraryItem | BUSINESS-SPECIFIC | Hotel/vehicle/ticket/activity lines (`travel_itinerary_items`) |
| TravelBookingDocument | BUSINESS-SPECIFIC | Passport/visa/ID metadata (`travel_booking_documents`; no binary) |
| TravelAgent | BUSINESS-SPECIFIC | Agent master (`travel_agents`; default commission %) |
| TravelCommissionEntry | BUSINESS-SPECIFIC | Per-booking commission (`travel_commission_entries`) |

## Implemented (BIZ-56 … BIZ-59)

- `tour_packages`: tenant-scoped code/name/destination/duration/base_price/gst + required `item_id` FK to untracked item
- `travel_bookings` + `travel_booking_payments` + number counter (`TB-#####`) + optional `agent_id`
- `travel_itinerary_items` + `travel_booking_documents` (cascade on booking delete; tenant-scoped)
- `travel_agents` + `travel_commission_entries` (unique per booking; PENDING/PAID/CANCELLED)
- Migrations: `20260826_biz56_…` … `20260826_biz59_travel_agent_commission`

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
