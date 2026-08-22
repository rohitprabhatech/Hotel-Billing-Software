# Common Module — Inventory

Flexible engine: simple qty, weight, volume, length, area, serial, batch/lot, expiry, variants.

Operations: receive, adjust, sale deduct, return, transfer, wastage, recipe consume.

**Batch/expiry** are generic (grocery/bakery), not Medical Store features.

Baseline today: `stock_quantity` + `stock_movements`.

## Barcode & UoM (BIZ-08)

Each catalog item may define:

| Field | Purpose |
|-------|---------|
| `barcode` | Scannable code — unique per tenant (case-insensitive) |
| `uom` | Base unit: `pcs`, `kg`, `g`, `l`, `ml`, `m`, `cm`, `box`, `pack` (default `pcs`) |
| `sku` | Internal stock-keeping id (existing) |

API lookup: `GET /api/v1/items/by-barcode/:code`, `GET /api/v1/items?barcode=`.

Compatible unit conversions (`kg↔g`, `l↔ml`, `m↔cm`) live in `app.utils.uom` for future industry packs.

Billing POS (`New Bill`) exposes a scan field that resolves barcode → add line item.
