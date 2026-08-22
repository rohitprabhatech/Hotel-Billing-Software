# Stationery Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Barcode / SKU | Industry | High | Common core + pack |
| Brand management | Industry | High | Common core + pack |
| Category management | Industry | High | Common core + pack |
| Bulk pricing | Industry | High | Common core + pack |
| Low-stock alerts | Industry | High | Common core + pack |
| Customer credit | Industry | High | Common core + pack |
| Fast POS billing | Industry | High | Common core + pack |
| Product search | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = stationery`.  
Implementation lives under backend/frontend `modules/stationery/` (conceptual — not created yet).
