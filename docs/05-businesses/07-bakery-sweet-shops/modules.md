# Bakery / Sweet Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Product production | Industry | High | Common core + pack |
| Ingredient inventory | Industry | High | Common core + pack |
| Batch management | Industry | High | Common core + pack |
| Expiry tracking | Industry | High | Common core + pack |
| Custom cake orders (size/flavor) | Industry | High | Common core + pack |
| Advance / remaining payment | Industry | High | Common core + pack |
| Delivery date/time | Industry | High | Common core + pack |
| Order status | Industry | High | Common core + pack |
| Wastage tracking | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = bakery_sweet`.  
Implementation lives under backend/frontend `modules/bakery/` (conceptual — not created yet).
