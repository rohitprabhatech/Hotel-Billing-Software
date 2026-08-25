# Clothing Shops — Database

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | `tracks_variants`; parent stock = sum of variants |
| Customer | COMMON ENTITY | Reused |
| Bill | COMMON ENTITY | Reused |
| BillItem | COMMON ENTITY | Optional `variant_id` |
| Payment | COMMON ENTITY | Reused |
| StockMovement | COMMON ENTITY | Reused |
| Notification | COMMON ENTITY | Low / out of stock on variant rows |
| AuditLog | COMMON ENTITY | CREATE/UPDATE/DELETE/REPLACE variants |
| BusinessSettings | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC ENTITIES

| Entity | Class | Purpose |
|--------|-------|---------|
| ItemVariant | BUSINESS-SPECIFIC | Size + color + optional brand, SKU, barcode, stock (`item_variants`) |
| ItemImage | BUSINESS-SPECIFIC | URL metadata + optional local `storage_key` (`item_images`) |
| SalesReturn | BUSINESS-SPECIFIC | Return/exchange header linked to original `Bill` |
| SalesReturnItem | BUSINESS-SPECIFIC | Qty returned + optional exchange variant |

Size/color/brand are attributes on `item_variants` in BIZ-25 (no separate master tables yet).

## Relationships (summary)

- `item_variants.tenant_id` RESTRICT to Tenant; `item_id` CASCADE to Item.
- Unique `(tenant_id, item_id, size, color)`; unique tenant SKU/barcode when present.
- `bill_items.variant_id` SET NULL on variant delete.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
