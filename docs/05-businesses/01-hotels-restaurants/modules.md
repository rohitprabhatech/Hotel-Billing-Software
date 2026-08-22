# Hotels / Restaurants — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Restaurant Menu (`restaurant_menu`) | Industry | High | BIZ-11 — item `is_menu` / `is_veg`, `GET /menu` |
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Table Management (Available / Occupied / Reserved) | Industry | High | Common core + pack |
| KOT | Industry | High | Common core + pack |
| Kitchen Dashboard | Industry | High | Common core + pack |
| Waiter Management | Industry | High | Common core + pack |
| Split Bill | Industry | High | Common core + pack |
| Merge Tables | Industry | High | Common core + pack |
| Recipes / Ingredient Stock | Industry | High | Common core + pack |
| Food Wastage | Industry | High | Common core + pack |
| Service Charge | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = hotel_restaurant`.  
Implementation lives under backend/frontend `modules/restaurant/` (conceptual — not created yet).
