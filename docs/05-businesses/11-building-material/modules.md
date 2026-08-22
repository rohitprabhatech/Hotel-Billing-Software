# Hardware / Building Material — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Multiple units | Industry | High | Common core + pack |
| Weight / length / area | Industry | High | Common core + pack |
| Bulk pricing | Industry | High | Common core + pack |
| Quotation | Industry | High | Common core + pack |
| Delivery challan | Industry | High | Common core + pack |
| Customer / supplier credit | Industry | High | Common core + pack |
| Transport charges | Industry | High | Common core + pack |
| Delivery management | Industry | High | Common core + pack |
| Warehouse stock | Industry | High | Common core + pack |
| Price history | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = building_material`.  
Implementation lives under backend/frontend `modules/building-material/` (conceptual — not created yet).
