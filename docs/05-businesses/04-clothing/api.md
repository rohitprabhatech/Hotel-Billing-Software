# Clothing Shops — API

Common `/bills`, `/customers`, `/items` stay the source of truth for billing and catalog.

## BIZ-25 — Size / color / brand variants

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/item-variants` | List tenant variants (`item_id`, page) | JWT | `variants` | `items.read` |
| GET | `/api/v1/items/{id}/variants` | List variants for one item | JWT | `variants` | `items.read` |
| POST | `/api/v1/items/{id}/variants` | Create size+color row (independent stock) | JWT | `variants` | `items.write` |
| PUT | `/api/v1/items/{id}/variants` | Replace matrix `{ variants: [...] }` | JWT | `variants` | `items.write` |
| PATCH | `/api/v1/items/{id}/variants/{variant_id}` | Update one row | JWT | `variants` | `items.write` |
| DELETE | `/api/v1/items/{id}/variants/{variant_id}` | Delete one row | JWT | `variants` | `items.write` |

Sell: `POST /api/v1/bills` line may include `variant_id`. Required when the item `tracks_variants`. Different size/color lines do not merge. Variant barcodes resolve via `GET /api/v1/items/by-barcode/{code}` (`matched_variant`).

Unique: size+color per item (case-insensitive). SKU/barcode unique per tenant when set. Parent `stock_quantity` is the sum of active variant stock.

## BIZ-26 — Product images and clothing POS

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/clothing/pos-catalog` | Items with variant matrix + primary image | JWT | `variants` | `items.read` |
| GET | `/api/v1/items/{id}/images` | List image metadata | JWT | `product_images` | `items.read` |
| POST | `/api/v1/items/{id}/images` | Add `image_url` (http/https) | JWT | `product_images` | `items.write` |
| POST | `/api/v1/items/{id}/images/upload` | Multipart file upload (≤2 MB) | JWT | `product_images` | `items.write` |
| DELETE | `/api/v1/items/{id}/images/{image_id}` | Remove image | JWT | `product_images` | `items.write` |
| GET | `/api/v1/item-images/files/{filename}` | Serve local file (unguessable name) | Public | — | — |

POS catalog `variants[]` include per-size/color `stock_quantity`. Billing still uses `variant_id` so the selected cell is the only stock that reduces.

## BIZ-27 — Returns and exchanges

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/returns/lookup` | Returnable lines for a bill (`bill_number` or `bill_id`) | JWT | `returns_exchange` | `billing` |
| GET | `/api/v1/returns` | List returns | JWT | `returns_exchange` | `billing` |
| GET | `/api/v1/returns/{id}` | Return detail | JWT | `returns_exchange` | `billing` |
| POST | `/api/v1/returns` | Finalize return or exchange | JWT (Owner/Manager) | `returns_exchange` | `billing` |

`kind=RETURN` restocks the original variant (or item). `kind=EXCHANGE` restocks the returned variant and deducts `exchange_variant_id`. Refund is proportional to the original line total (simple GST). Billing users may look up/list but cannot POST.

## BIZ-28 — Apparel reports and customer history

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/clothing/sales` | Sales by brand/size/color/category, variant stock, returns totals | JWT (Owner/Manager) | `variants` | `reports` |
| GET | `/api/v1/clothing/customer-history` | Customer bills with variant line items | JWT | `variants` | `customers.read` |

Query params for sales: `date`, `from`/`to`, `payment_method`, `brand`, `size`, `color`, `category_id`. Brand/size/color join `bill_items.variant_id` → `item_variants`. Audit: `VIEW_CLOTHING_REPORT`, `VIEW_CLOTHING_CUSTOMER_HISTORY`.

## Later clothing APIs

Dedicated size/color/brand master tables are not in this pack.

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts.
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
