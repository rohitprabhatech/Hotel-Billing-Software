# Grocery Stores / Kirana — API

Namespace: `/api/v1/grocery/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those for billing and master data.

## BIZ-20 — Fast POS

| Method | Endpoint | Purpose | Auth | Module | Permission |
|--------|----------|---------|------|--------|------------|
| GET | `/api/v1/grocery/pos-catalog` | Active items for scan POS (barcode, UoM, stock) | JWT | `barcode_pos` | `items.read` |

Barcode lookup at billing time: `GET /api/v1/items/by-barcode/{code}` (BIZ-08). Bill creation: `POST /api/v1/bills` with decimal `quantity` for weight UoMs.

## Planned (later sprints)

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/grocery/credit/{customer_id}` | Credit balance / charge | JWT | industry + role | Yes |
| POST | `/api/v1/grocery/credit/{customer_id}/pay` | Settle credit | JWT | industry + role | Yes |
| GET | `/api/v1/grocery/expiry` | Near-expiry batches | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
