# Bakery / Sweet Shops — Database

> Production tables implemented in BIZ-40. Remaining entities stay conceptual until later sprints.

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | Ingredients + finished goods |
| Recipe / RecipeIngredient | COMMON (BIZ-16) | BOM for production |
| Customer | COMMON ENTITY | Reused |
| Bill | COMMON ENTITY | Reused |
| StockMovement | COMMON ENTITY | `source=PRODUCTION` |
| Notification | COMMON ENTITY | Low / out-of-stock on ingredients |
| AuditLog | COMMON ENTITY | `CREATE_PRODUCTION` |
| WastageEntry | COMMON (BIZ-18) | Shared wastage |

## BUSINESS-SPECIFIC ENTITIES

| Entity | Class | Purpose | Status |
|--------|-------|---------|--------|
| CakeOrder / CustomProductOrder | BUSINESS-SPECIFIC | Shared custom order (`order_type=bakery`) | BIZ-42 |
| CustomOrderPayment | BUSINESS-SPECIFIC | Advance payment ledger lines | BIZ-42 |
| ProductionRun | BUSINESS-SPECIFIC | Bake / production batch header (`PR-#####`) | BIZ-40 |
| ProductionRunItem | BUSINESS-SPECIFIC | Ingredient consumption lines | BIZ-40 |
| ProductionRunNumberCounter | BUSINESS-SPECIFIC | Per-tenant run numbers | BIZ-40 |


## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- `ProductionRun.recipe_id` → `recipes`; `finished_item_id` → `items`.
- Ingredient and FG stock changes linked via `stock_movements` (`reference_type=PRODUCTION`).

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
