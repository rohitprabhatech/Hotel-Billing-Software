# Stationery Shops — Modules

Activated when `business_type = stationery` (see `BUSINESS_TYPE_MODULES` in backend).

| Module code | Type | Priority | Notes |
|-------------|------|----------|-------|
| `barcode_pos` | Industry | High | POS catalog + barcode lookup |
| `bulk_pricing` | Industry | High | Shared bulk tiers on items/bills |
| `customer_credit` | Industry | High | Udhari / outstanding + credit bills |
| Billing / Inventory / Customers / Reports | Common | High | Shared core |

Also available via common inventory: low-stock alerts on sell/purchase paths.

Brand/category management uses common Categories + Items (no separate stationery brands API in BIZ-44).
