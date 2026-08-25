# Grocery Stores / Kirana — API

Namespace: `/api/v1/grocery/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those for billing and master data.

## BIZ-20 — Fast POS

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/grocery/pos-catalog` | Active items for scan POS (barcode, UoM, stock, price tiers) | JWT | `barcode_pos` | `items.read` |

Barcode lookup at billing time: `GET /api/v1/items/by-barcode/{code}` (BIZ-08). Bill creation: `POST /api/v1/bills` with decimal `quantity` for weight UoMs. When `bulk_pricing` is enabled, unit price is resolved from item price tiers.

## BIZ-21 — Bulk price tiers

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/items/{id}/price-tiers` | List tiers | JWT | `bulk_pricing` | `items.read` |
| POST | `/api/v1/items/{id}/price-tiers` | Create one tier | JWT | `bulk_pricing` | `items.write` |
| PUT | `/api/v1/items/{id}/price-tiers` | Replace all tiers | JWT | `bulk_pricing` | `items.write` |
| DELETE | `/api/v1/items/{id}/price-tiers/{tier_id}` | Delete tier | JWT | `bulk_pricing` | `items.write` |

Tier rule: highest `min_quantity` ≤ line qty wins; otherwise item base `price`.

## BIZ-22 — Batches / expiry

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/batches` | List batches (`item_id`, `status=expired\|expiring\|ok`) | JWT | `batch_expiry` | `items.read` |
| GET | `/api/v1/batches/expiry` | Near-expiry + expired report | JWT | `batch_expiry` | `items.read` |
| GET | `/api/v1/grocery/expiry` | Alias of batches expiry | JWT | `batch_expiry` | `items.read` |
| POST | `/api/v1/batches` | Receive batch (qty + expiry_date) | JWT | `batch_expiry` | `items.stock` |
| POST | `/api/v1/batches/{id}/adjust` | Adjust batch qty (**reason required**) | JWT | `batch_expiry` | `items.stock` |

Item flags: `tracks_batches`, `block_expired_batches`. When both on, billing uses FEFO and blocks sales beyond non-expired qty. Grocery tenants require a reason on `POST /items/{id}/adjust-stock`.

## BIZ-23 — Credit / udhari and sales

Credit posting reuses common `POST /api/v1/bills` with `payment_method=credit` and `customer_id` (BIZ-09 ledger). Grocery aliases below are gated by `customer_credit`.

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/grocery/outstanding` | Customers with outstanding balance | JWT | `customer_credit` | `customers.read` |
| GET | `/api/v1/grocery/credit/{customer_id}` | Balance + payment/credit history | JWT | `customer_credit` | `customers.read` |
| POST | `/api/v1/grocery/credit/{customer_id}/pay` | Collect against outstanding | JWT | `customer_credit` | `customers.write` |
| GET | `/api/v1/grocery/sales` | Daily sales (incl. credit mix) + outstanding totals | JWT | `barcode_pos` | `reports` |

Charge on credit: `POST /api/v1/bills` (not a separate grocery charge endpoint). Collections also work via `POST /api/v1/customers/{id}/payments`.

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
