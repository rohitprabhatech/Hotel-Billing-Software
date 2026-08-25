# Clothing Shops — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
| Billing | Common | High | Auth, Products |
| Inventory | Common | High | Products |
| Customers | Common | High | Tenant |
| Payments | Common | High | Billing |
| Reports | Common | High | Billing data |
| `variants` | Industry | High | Items + barcode (BIZ-08) |
| `product_images` | Industry | High | Items (BIZ-26) |
| `returns_exchange` | Industry | High | Bills + variants (BIZ-27) |
| Exchange / Return | Industry | High | BIZ-27 |
| Apparel reports (`/clothing/sales`) | Industry | High | BIZ-28 |

`variants` is on the clothing (and hardware) default pack. Size, color, and brand are stored on each variant row in BIZ-25.

## Purpose summary

This pack activates when `business_type = clothing`. Variant CRUD lives on `/items/:id/variants` and `/item-variants`, not a separate `/clothing` namespace.
