# Bakery / Sweet Shops — API

Namespace notes for industry extensions. Prefer shared core endpoints where noted.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/custom-orders` | Shared custom orders (`order_type=bakery`) | JWT | `billing` + `custom_orders` | Yes |
| PATCH | `/api/v1/custom-orders/{id}/status` | Status pipeline (Owner/Manager) | JWT | `billing` | Yes |
| POST | `/api/v1/custom-orders/{id}/advance` | Record advance payment | JWT | `billing` | Yes |
| GET/POST | `/api/v1/bakery/cake-orders` | Bakery aliases | JWT | same | Yes |
| POST | `/api/v1/bakery/cake-orders/{id}/advance` | Advance alias | JWT | same | Yes |
| GET/POST | `/api/v1/productions` | Production runs (BOM consume + FG stock) | JWT | `production.*` | Yes |
| GET | `/api/v1/bakery/expiry` | Near-expiry / expired FG batches | JWT | `items.read` + `batch_expiry` | Yes |
| GET/POST | `/api/v1/batches` | Shared batch receive / list | JWT | `items.*` + `batch_expiry` | Yes |
| GET/POST | `/api/v1/recipes` | Shared recipes (BOM) | JWT | `recipes.*` | Yes |
| GET/POST | `/api/v1/wastage` | Shared wastage write-off | JWT | `wastage.*` | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Custom order create:** `{ title, total_amount, size?, flavor?, advance_amount?, delivery_at?, ... }` — initial advance must be **less than** total (`CO-#####`).
- **Status:** BOOKED → CONFIRMED → IN_PRODUCTION → READY → DELIVERED (or CANCELLED).
- **Errors:** 401 / 403 / 404 / 400.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
