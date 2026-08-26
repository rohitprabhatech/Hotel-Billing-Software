# Hardware Stores — API

Namespace: `/api/v1/hardware/...` (module gate: `uom_measurement`; also used by building material).

Common `/bills`, `/customers`, `/items` remain the primary write path; quote helpers feed Hardware POS.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/hardware/units` | UoM catalog (length/weight/area/etc.) | JWT | items.read | Yes |
| GET | `/api/v1/hardware/pos-catalog` | Active items with sale UoM + qty step | JWT | items.read | Yes |
| POST | `/api/v1/hardware/quote` | Line quote: qty × unit price (+ stock convert) | JWT | billing | Yes |
| POST | `/api/v1/hardware/convert` | Convert quantity between compatible UoMs | JWT | items.read | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Module:** `403` when `uom_measurement` is off (e.g. restaurant).
- **Quote body:** `{ "item_id", "quantity" }` → `unit_price`, `line_total`, `sale_uom`, `stock_quantity_deducted`.
- **Price:** item price is per **sale_uom** (defaults to stock `uom`).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
