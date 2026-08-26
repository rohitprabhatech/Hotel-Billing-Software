# Travel Agencies — Frontend

| Page | Path | Roles | Notes |
|------|------|-------|-------|
| Tour Packages | `/owner/tour-packages` | Owner / Manager write; Billing read + bill | Module `tour_packages` |
| Travel Bookings | `/owner/travel-bookings` | Owner / Manager status + details; Billing create + pay | Module `travel_bookings` |
| Travel Agents | `/owner/travel-agents` | Owner / Manager write; report for billing | Module `travel_commission` |
| Customers / Bills | shared | As permitted | Common core |

## UX (BIZ-56 … BIZ-59)

- Create packages with code, destination, duration, price, GST
- Cards show service pricing; **Create bill** sells without stock
- Linked catalog item stays untracked (`stock_quantity = null`)
- Booking board: Booked → Confirmed → In progress → Completed; advances + remaining payments
- Booking **Details** dialog: Itinerary tab (hotel/vehicle/ticket/activity) + Documents tab (metadata only)
- Optional agent on booking create; Agents page with commission report by agent + mark paid

## Responsive

Mobile + desktop; dark mode via existing theme.
