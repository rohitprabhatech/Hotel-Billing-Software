# Book Stores — Database

> Implemented in BIZ-45 as columns on common `items` (not a separate BookMetadata table).

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
| Tenant | COMMON ENTITY | Reused |
| User | COMMON ENTITY | Reused |
| Role | COMMON ENTITY | Reused |
| Category | COMMON ENTITY | Reused |
| Product / Item | COMMON ENTITY | Extended with book fields |
| Customer / Bill / Payment / StockMovement / AuditLog | COMMON ENTITY | Reused |

## BUSINESS-SPECIFIC (on `items`)

| Column | Type | Notes |
|--------|------|-------|
| `isbn` | String(32), nullable | Unique per tenant (`uq_items_tenant_isbn`); stored without hyphens/spaces |
| `author` | String(160), nullable | Indexed with tenant for search |
| `publisher` | String(160), nullable | Free text |

Migration: `20260826_biz45_book_store_metadata`

Returns remain on shared returns module (BIZ-46).

## See also

[`../../03-database/04-business-specific-tables.md`](../../03-database/04-business-specific-tables.md) · [`../../03-database/03-common-tables.md`](../../03-database/03-common-tables.md)
