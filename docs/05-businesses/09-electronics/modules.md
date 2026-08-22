# Electronics Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Serial number | Industry | High | Common core + pack |
| Warranty tracking | Industry | High | Common core + pack |
| Product model / brand | Industry | High | Common core + pack |
| Barcode | Industry | High | Common core + pack |
| Exchange / Return | Industry | High | Common core + pack |
| Repair / service | Industry | High | Common core + pack |
| Installation tracking | Industry | High | Common core + pack |
| Customer purchase history | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = electronics`.  
Implementation lives under backend/frontend `modules/electronics/` (conceptual — not created yet).
