# Hardware Stores — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Unit management | Industry | High | Common core + pack |
| Weight / length based products | Industry | High | Common core + pack |
| Bulk quantity | Industry | High | Common core + pack |
| Brand management | Industry | High | Common core + pack |
| Product variants | Industry | High | Common core + pack |
| Low-stock alerts | Industry | High | Common core + pack |
| Customer / supplier credit | Industry | High | Common core + pack |
| Price history | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = hardware`.  
Implementation lives under backend/frontend `modules/hardware/` (conceptual — not created yet).
