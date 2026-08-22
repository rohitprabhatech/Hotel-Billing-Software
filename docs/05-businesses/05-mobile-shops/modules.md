# Mobile Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| IMEI number | Industry | High | Common core + pack |
| Serial number | Industry | High | Common core + pack |
| Mobile model / brand | Industry | High | Common core + pack |
| Warranty tracking | Industry | High | Common core + pack |
| Accessories management | Industry | High | Common core + pack |
| Mobile exchange | Industry | High | Common core + pack |
| Repair / service tracking | Industry | High | Common core + pack |
| Customer purchase history | Industry | High | Common core + pack |
| Stock by IMEI | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = mobile`.  
Implementation lives under backend/frontend `modules/mobile/` (conceptual — not created yet).
