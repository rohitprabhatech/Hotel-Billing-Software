# Wholesale Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Wholesale / retail / customer-wise pricing | Industry | High | Common core + pack |
| Bulk quantity | Industry | High | Common core + pack |
| Credit / Udhari | Industry | High | Common core + pack |
| Payment tracking | Industry | High | Common core + pack |
| Outstanding reports | Industry | High | Common core + pack |
| Multiple warehouses | Industry | High | Common core + pack |
| Stock transfer | Industry | High | Common core + pack |
| Purchase order / Sales order | Industry | High | Common core + pack |
| Quotation / Delivery challan | Industry | High | Common core + pack |
| Barcode | Industry | High | Common core + pack |
| GST invoice | Industry | High | Common core + pack |

## Purpose summary

This pack activates only when `business_type = wholesale`.  
Implementation lives under backend/frontend `modules/wholesale/` (conceptual — not created yet).
