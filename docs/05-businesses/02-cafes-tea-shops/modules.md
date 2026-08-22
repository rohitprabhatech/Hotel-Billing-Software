# Cafes / Tea Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Optional Tables / KOT | Industry | High | Common core + pack |
| Add-ons | Industry | High | Common core + pack |
| Combo offers | Industry | High | Common core + pack |
| Discount / coupon | Industry | High | Common core + pack |
| Popular-item report | Industry | High | Common core + pack |
| Ingredient stock | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = cafe_tea`.  
Implementation lives under backend/frontend `modules/cafe/` (conceptual — not created yet).
