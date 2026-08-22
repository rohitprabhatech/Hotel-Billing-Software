# Hardware / Building Material — Database

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
| Warehouse | BUSINESS-SPECIFIC | Location |
| StockTransfer | BUSINESS-SPECIFIC | Inter-warehouse |
| Quotation | BUSINESS-SPECIFIC | Trade quote |
| DeliveryChallan | BUSINESS-SPECIFIC | Challan |
| TransportCharge | BUSINESS-SPECIFIC | Freight line/fee |
| CreditAccount | BUSINESS-SPECIFIC | Credit |
| PriceHistory | BUSINESS-SPECIFIC | Prices |

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
