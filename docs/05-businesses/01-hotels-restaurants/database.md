# Hotels / Restaurants — Database

> Conceptual only. No tables created in documentation phase.

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | Reused |
| Customer | COMMON ENTITY | Reused |
| Bill | COMMON ENTITY | Reused |
| BillItem | COMMON ENTITY | Reused |
| Payment | COMMON ENTITY | Reused |
| StockMovement | COMMON ENTITY | Reused |
| Notification | COMMON ENTITY | Reused |
| AuditLog | COMMON ENTITY | Reused |
| BusinessSettings | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC ENTITIES

| Entity | Class | Purpose |
|--------|-------|---------|
| RestaurantTable | BUSINESS-SPECIFIC | Floor tables with status — **implemented** as `dining_tables` (BIZ-12) |
| DiningOrder | BUSINESS-SPECIFIC | Order linked to table/session — **implemented** as `orders` / `order_items` (BIZ-13) |
| KOT | BUSINESS-SPECIFIC | Kitchen order ticket header |
| KOTItem | BUSINESS-SPECIFIC | Lines on a KOT |
| KitchenTicket | BUSINESS-SPECIFIC | Kitchen queue view state |
| WaiterAssignment | BUSINESS-SPECIFIC | Optional waiter on table/order |
| Recipe | BUSINESS-SPECIFIC | Finished item → recipe |
| RecipeIngredient | BUSINESS-SPECIFIC | Ingredient quantities |
| WastageEntry | BUSINESS-SPECIFIC | Food wastage log |

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
