# Clothing Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Size management (S–XXL) | Industry | High | Common core + pack |
| Color management | Industry | High | Common core + pack |
| Brand management | Industry | High | Common core + pack |
| Barcode / SKU | Industry | High | Common core + pack |
| Product images | Industry | High | Common core + pack |
| Size-wise / color-wise stock | Industry | High | Common core + pack |
| Exchange / Return | Industry | High | Common core + pack |
| Sales by brand / category | Industry | High | Common core + pack |
| Customer purchase history | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = clothing`.  
Implementation lives under backend/frontend `modules/clothing/` (conceptual — not created yet).
