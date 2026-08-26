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
| Quotation / QuotationItem | BUSINESS-SPECIFIC (BIZ-36) | Trade quote → bill |
| DeliveryChallan / DeliveryChallanItem | BUSINESS-SPECIFIC (BIZ-36) | Dispatch document + PDF |
| Warehouse / WarehouseStock | BUSINESS-SPECIFIC (BIZ-38) | Multi-location balances |
| StockTransfer / StockTransferItem | BUSINESS-SPECIFIC (BIZ-38) | Inter-warehouse moves |
| TransportCharge | via bill/challan fields (BIZ-37) | Freight fee |
| CreditAccount | SHARED LEDGER | Credit (BIZ-09 / BIZ-37) |

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
