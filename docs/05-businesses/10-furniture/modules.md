# Furniture Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Product dimensions / material / color | Industry | High | Common core + pack |
| Custom furniture orders | Industry | High | Common core + pack |
| Advance / remaining payment | Industry | High | Common core + pack |
| Delivery management | Industry | High | Common core + pack |
| Installation tracking | Industry | High | Common core + pack |
| Order status | Industry | High | Common core + pack |
| Customer quotation | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = furniture`.  
Implementation lives under backend/frontend `modules/furniture/` (conceptual — not created yet).
