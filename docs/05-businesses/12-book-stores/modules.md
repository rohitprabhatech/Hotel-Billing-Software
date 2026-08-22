# Book Stores — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| ISBN | Industry | High | Common core + pack |
| Author / Publisher / Edition | Industry | High | Common core + pack |
| Barcode | Industry | High | Common core + pack |
| Book category | Industry | High | Common core + pack |
| Stock management | Industry | High | Common core + pack |
| Bulk pricing | Industry | High | Common core + pack |
| Customer purchase history | Industry | High | Common core + pack |
| Return management | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = book_store`.  
Implementation lives under backend/frontend `modules/books/` (conceptual — not created yet).
