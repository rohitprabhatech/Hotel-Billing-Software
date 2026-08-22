# Common Module — Purchases

**Status:** Implemented (BIZ-06)

Record supplier purchases that increase inventory, update item cost price, and write stock movement ledger rows.

## Capabilities

| Action | Owner | Manager | Billing User |
|--------|:-----:|:-------:|:------------:|
| List / view purchases | ✅ | ✅ | ❌ |
| Create purchase | ✅ | ✅ | ❌ |
| Cancel purchase | ✅ | ✅ | ❌ |

Permissions: `purchases.read`, `purchases.write`.

## Data model

- **purchases** — header with `purchase_number` (`PO-{seq}`), optional supplier, invoice number, notes, total, status (`FINALIZED` / `CANCELLED`).
- **purchase_items** — line items with quantity, unit cost, line total; item name snapshot.
- **purchase_number_counters** — per-tenant PO sequence.

All entities are tenant-scoped via `tenant_id` from JWT context.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/purchases` | List with `status`, `supplier_id`, `q`, pagination |
| POST | `/api/v1/purchases` | Create purchase (atomic stock increase) |
| GET | `/api/v1/purchases/:id` | Purchase detail with line items |
| POST | `/api/v1/purchases/:id/cancel` | Reverse stock (requires reason) |

## Stock & ledger

On create:

1. Row-lock items in stable sorted order (same pattern as billing).
2. Increase `item.stock_quantity` and set `item.cost_price` to line unit cost.
3. Record `StockMovement` with `source=PURCHASE`, `reference_type=PURCHASE`.

On cancel:

1. Row-lock affected items.
2. Decrease stock by purchased quantities; blocked if result would be negative (`409`).
3. Record `StockMovement` with `source=PURCHASE_CANCEL`.

Low-stock notifications fire when restocking clears a threshold (existing notification service).

## Frontend

- Owner: `/owner/purchases`
- Manager: `/billing/purchases`

Purchase form supports optional supplier, invoice number, notes, and multi-line items (item picker, qty, unit cost). Detail view and cancel-with-reason for finalized POs.

## Audit

`CREATE_PURCHASE` and `CANCEL_PURCHASE` actions logged via audit service.

## Related

- Supplier master (BIZ-05) — optional linkage on purchase header
- Stock movements ledger — `PURCHASE` / `PURCHASE_CANCEL` sources
- Ad-hoc receive-stock remains available for non-PO receipts
