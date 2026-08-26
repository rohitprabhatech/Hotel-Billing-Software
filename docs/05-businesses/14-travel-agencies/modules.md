# Travel Agencies — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Tour package management | Industry | High | Common core + pack |
| Package pricing | Industry | High | Common core + pack |
| Booking management | Industry | High | Common core + pack |
| Advance / remaining payment | Industry | High | Common core + pack |
| Booking status | Industry | High | Common core + pack |
| Hotel / vehicle / ticket details | Industry | High | Common core + pack |
| Customer documents | Industry | High | Common core + pack |
| Travel itinerary | Industry | High | Common core + pack |
| Agent / commission management | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = travel_agency`.
Tour packages API/UI live under `/tour-packages`, `/travel/packages`, and `/owner/tour-packages` (BIZ-56).
Bookings board + nested itinerary/documents under `/travel-bookings`, `/travel/bookings`, and `/owner/travel-bookings` (BIZ-57 / BIZ-58).
Agents + commission report under `/travel-agents`, `/commissions`, `/travel/agents|commissions`, and `/owner/travel-agents` (BIZ-59; module `travel_commission`).
