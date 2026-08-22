# Grocery Stores / Kirana — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Barcode scanner flow | Industry | High | Common core + pack |
| Unit management (kg, g, L, piece) | Industry | High | Common core + pack |
| Low-stock alerts | Industry | High | Common core + pack |
| Stock adjustment | Industry | High | Common core + pack |
| Customer credit / Udhari | Industry | High | Common core + pack |
| Customer payment history | Industry | High | Common core + pack |
| Bulk pricing | Industry | High | Common core + pack |
| Expiry tracking (generic inventory) | Industry | High | Common core + pack |
| Fast POS billing | Industry (`barcode_pos`) | High | BIZ-08 barcode, BIZ-10 billing — **BIZ-20 done** |

## Purpose summary

This pack activates only when `business_type = grocery_kirana`.  
Fast POS: `backend/app/routes/grocery_routes.py`, `frontend/src/pages/modules/GroceryPosPage.jsx`.
