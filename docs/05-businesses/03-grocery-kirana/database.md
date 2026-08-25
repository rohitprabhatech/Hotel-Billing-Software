# Grocery Stores / Kirana — Database

> Conceptual only. No tables created in documentation phase.

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | Reused |
| Customer | COMMON ENTITY | Reused (`balance`, `credit_limit`) |
| PartyLedgerEntry | COMMON ENTITY | BIZ-09 udhari ledger reused by grocery |
| Bill | COMMON ENTITY | Reused (`payment_method=credit`) |
| BillItem | COMMON ENTITY | Reused |
| Payment | COMMON ENTITY | Reused |
| StockMovement | COMMON ENTITY | Reused |
| Notification | COMMON ENTITY | Reused |
| AuditLog | COMMON ENTITY | Reused |
| BusinessSettings | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC ENTITIES

Grocery credit does **not** add a separate credit-account table. Outstanding is `customers.balance` plus `party_ledger_entries` (BIZ-09).

| Entity | Class | Purpose |
|--------|-------|---------|
| BulkPriceTier | BUSINESS-SPECIFIC | Qty-based pricing (BIZ-21 `item_price_tiers`) |
| ItemBatch | BUSINESS-SPECIFIC | Expiry lots (BIZ-22 `item_batches`) |

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
