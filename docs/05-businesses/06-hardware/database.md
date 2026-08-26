# Hardware Stores — Database

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
| Item.sale_uom | COMMON EXTENSION (BIZ-35) | Optional sell unit; stock remains `items.uom` |
| Unit catalog | CONSTANT | `app.constants.uom` / measurement helpers (not a table) |
| PriceHistory | BUSINESS-SPECIFIC | Historical unit prices (later) |
| CreditAccount | BUSINESS-SPECIFIC | Customer/supplier credit (shared ledger) |

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
