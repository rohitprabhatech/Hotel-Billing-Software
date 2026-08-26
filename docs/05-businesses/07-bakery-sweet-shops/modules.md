# Bakery / Sweet Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High* | Products (*light/none for Travel) |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| Product production | Industry | High | Common core + pack |
| Ingredient inventory | Industry | High | Common core + pack |
| Batch management | Industry | High | Common core + pack |
| Expiry tracking | Industry | High | Common core + pack |
| Custom cake orders (size/flavor) | Industry | High | Common core + pack |
| Advance / remaining payment | Industry | High | Common core + pack |
| Delivery date/time | Industry | High | Common core + pack |
| Order status | Industry | High | Common core + pack |
| Wastage tracking | Industry | High | Common core + pack |

## Purpose summary

This pack activates when `business_type = bakery_sweet`.

**Enabled modules (defaults):** `production`, `recipe`, `batch_expiry`, `custom_orders`, `wastage`.

| Code | Implemented |
|------|-------------|
| `recipe` | Shared BIZ-16 (bakery may link BOM to non-menu FG items) |
| `production` | BIZ-40 `/productions` + Owner Production page |
| `wastage` | Shared BIZ-18; BIZ-41 FEFO write-off on batch-tracked FG |
| `batch_expiry` | Shared BIZ-22; BIZ-41 bakery enablement + production→batch |
| `custom_orders` | BIZ-42 shared `custom_product_orders` (type=bakery) |