# Indexes and Performance

Always index `(tenant_id, …)` on hot tables. Unique per tenant: email, SKU, bill_number, IMEI/ISBN as applicable. Follow `parent_key` pattern for nullable hierarchy uniques.

## Index plan (BIZ-66)

| Index | Table | Columns | Serves |
|-------|--------|---------|--------|
| `uq_items_tenant_barcode` | items | `(tenant_id, barcode)` | Exact barcode POS scan |
| `ix_items_tenant_active_name` | items | `(tenant_id, is_active, name)` | Active catalog list/order |
| `uq_serial_units_tenant_serial` | serial_units | `(tenant_id, serial)` | Exact serial / IMEI scan |
| `ix_serial_units_tenant_item_status` | serial_units | `(tenant_id, item_id, status)` | Per-item stock board |
| `ix_serial_units_tenant_status_received` | serial_units | `(tenant_id, status, received_at)` | Status-only lists |
| `uq_warehouse_stocks_tenant_wh_item` | warehouse_stocks | `(tenant_id, warehouse_id, item_id)` | Per-WH balance |
| `ix_warehouse_stocks_tenant_item` | warehouse_stocks | `(tenant_id, item_id)` | Cross-WH qty by item |
| `ix_stock_movements_tenant_item_created` | stock_movements | `(tenant_id, item_id, created_at)` | Item ledger |
| `ix_bills_tenant_created_at` | bills | `(tenant_id, created_at)` | Recent bills |
| `ix_bills_tenant_status_created_at` | bills | `(tenant_id, status, created_at)` | Report filters |

Alembic: `20260827_cafe_coupons` (head; includes `20260826_biz66_perf_indexes`). Ops catch-up: `backend/scripts/apply_perf_indexes.py`.

### Notes

- Fuzzy POS `q` (`ILIKE %term%`) cannot use B-tree indexes — bound with `POS_CATALOG_MAX_LIMIT` (100).
- Prefer exact barcode/serial path for scan speed; store barcodes trimmed (lookup already case-folds).

## Query budgets

| Path | Budget |
|------|--------|
| POS catalog `limit` | default **50**, max **100** |
| Items list `per_page` | max **100** |
| Menu items list | hard cap **500** |
| POS search p95 (staging) | **≤ 200 ms** (barcode exact + short `q`) |

Constants: `backend/app/constants/perf.py`.

## Frontend

Industry routes are already `React.lazy` in `AppRoutes.jsx`. POS grids stay ≤100 rows; virtualization deferred until staging shows DOM jank.
