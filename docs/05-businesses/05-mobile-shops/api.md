# Mobile Shops — API

Namespace: `/api/v1/mobile/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/serial-units` | IMEI inventory (shared) | JWT | `serial_imei` | Yes |
| GET/POST | `/api/v1/repairs` | Repair tickets (shared) | JWT | `repair_service` | Yes |
| GET | `/api/v1/mobile/sales` | Sales by brand/model + IMEI stock | JWT Owner/Manager | `serial_imei` + reports | Yes |
| GET | `/api/v1/mobile/customer-history` | Customer bills with IMEI lines | JWT | `serial_imei` + customers | Yes |

Item catalog fields for this pack: `brand`, `model_name` on `PUT/POST /items` (optional strings).

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
