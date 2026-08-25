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
| Customer credit / Udhari | Industry (`customer_credit`) | High | BIZ-09 ledger + BIZ-23 grocery POS — **done** |
| Customer payment history | Industry (`customer_credit`) | High | BIZ-23 grocery credit page — **done** |
| Bulk pricing | Industry (`bulk_pricing`) | High | BIZ-21 item_price_tiers — **done** |
| Expiry tracking (generic inventory) | Industry (`batch_expiry`) | High | BIZ-22 item_batches — **done** |
| Fast POS billing | Industry (`barcode_pos`) | High | BIZ-08 barcode, BIZ-10 billing — **BIZ-20 done** |

## Purpose summary

This pack activates only when `business_type = grocery_kirana`.  
Fast POS: `backend/app/routes/grocery_routes.py`, `frontend/src/pages/modules/GroceryPosPage.jsx`.
