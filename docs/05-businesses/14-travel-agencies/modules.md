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
Implementation lives under backend/frontend `modules/travel/` (conceptual — not created yet).
