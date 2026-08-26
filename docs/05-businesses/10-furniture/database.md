# Furniture Shops — Database

> BIZ-47: furniture specs live as columns on common `items` (not a separate FurnitureSpec table).

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant / User / Role | COMMON ENTITY | Reused |
| Category / Item | COMMON ENTITY | Item extended with furniture fields |
| Customer / Bill / Payment / StockMovement / AuditLog | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC (on `items` — BIZ-47)

| Column | Type | Notes |
|--------|------|-------|
| `dimension_length` | Numeric(12,3), nullable | L |
| `dimension_width` | Numeric(12,3), nullable | W |
| `dimension_height` | Numeric(12,3), nullable | H |
| `material` | String(120), nullable | Indexed with tenant |
| `color` | String(80), nullable | Catalog finish color |

Migration: `20260826_biz47_furniture_product_attributes`

## Custom orders (BIZ-48)

Reuses shared `custom_product_orders` / `custom_order_payments` with `order_type=furniture` (no new tables). Freeform dims/material map to `size` / `flavor`; catalog L/W/H stay on items.

Later pack entities (quotes, delivery, installation) reuse shared modules from prior phases.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
