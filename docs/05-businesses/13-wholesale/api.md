# Wholesale Shops — API

Shared billing uses `/api/v1/bills` with price-list resolution when `price_lists` module is on.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/price-lists` | Price list CRUD | JWT | items read/write + `price_lists` | Yes |
| GET/PATCH/DELETE | `/api/v1/price-lists/{id}` | Detail / update / delete | JWT | as above | Yes |
| PUT | `/api/v1/price-lists/{id}/items` | Replace item → unit price matrix | JWT | items.write | Yes |
| GET | `/api/v1/price-lists/customer-assignments` | Customer → list map | JWT | items.read | Yes |
| PUT/DELETE | `/api/v1/price-lists/customer-assignments/{customer_id}` | Assign / unassign | JWT | items.write | Yes |
| GET/POST | `/api/v1/wholesale/price-lists` | Wholesale aliases | JWT | as above | Yes |
| GET | `/api/v1/grocery/pos-catalog?customer_id=` | POS catalog with resolved `base_price` | JWT | items.read | Yes |
| GET/POST | `/api/v1/sales-orders` | Sales orders (`SO-#####`) | JWT | billing + `sales_orders` | Yes |
| PATCH | `/api/v1/sales-orders/{id}/status` | DRAFT/CONFIRMED/CANCELLED | JWT | Owner/Manager | Yes |
| POST | `/api/v1/sales-orders/{id}/convert` | Full convert → bill | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/purchase-orders` | Purchase orders (`PO-#####`) | JWT | purchases + `purchase_orders` | Yes |
| PATCH | `/api/v1/purchase-orders/{id}/status` | DRAFT/CONFIRMED/CANCELLED | JWT | Owner/Manager | Yes |
| POST | `/api/v1/purchase-orders/{id}/convert` | Full convert → purchase | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/wholesale/sales-orders` | SO aliases | JWT | as above | Yes |
| GET/POST | `/api/v1/wholesale/purchase-orders` | PO aliases | JWT | as above | Yes |
| GET/POST | `/api/v1/warehouses` | Warehouse CRUD | JWT | items + `warehouse` | Yes |
| GET | `/api/v1/warehouses/stocks` | Balances (`warehouse_id` / `item_id` filters) | JWT | items.read | Yes |
| GET/POST | `/api/v1/stock-transfers` | Stock transfers (`ST-#####`) | JWT | items.stock | Yes |
| GET/POST | `/api/v1/wholesale/warehouses` | Warehouse aliases | JWT | as above | Yes |
| GET/POST | `/api/v1/wholesale/stock-transfers` | Transfer aliases | JWT | as above | Yes |
| POST | `/api/v1/bills` | Optional `warehouse_id` when module on | JWT | billing | Yes |
| GET | `/api/v1/reports/outstanding` | Aged customer + supplier outstanding | JWT | reports (Owner/Manager) | Yes |
| GET | `/api/v1/wholesale/reports/outstanding` | Outstanding alias | JWT | reports | Yes |
| GET/POST | `/api/v1/wholesale/challans` | Challan aliases | JWT | billing + `delivery_challan` | Yes |
| GET | `/api/v1/bills/{id}/pdf` | Tax invoice PDF (TAX INVOICE when GST/wholesale) | JWT | billing | Yes |

## Resolution order (price lists)

1. Customer-assigned price list item price
2. Default **WHOLESALE** price list item price
3. Bulk quantity tiers (`bulk_pricing`, BIZ-21) on catalog retail
4. Catalog retail (`items.price`)

## Contract notes

- SO/PO convert is full-document only (no partial fulfillment in v1).
- Billing users can list SO/PO; Owner/Manager write and convert.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
