# Hotels / Restaurants — API

Namespace: `/api/v1/restaurant/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/restaurant/tables` | List/create tables | JWT | industry + role | Yes |
| PUT | `/api/v1/restaurant/tables/{id}` | Update status / merge | JWT | industry + role | Yes |
| POST | `/api/v1/restaurant/orders` | Create dining order | JWT | industry + role | Yes |
| POST | `/api/v1/restaurant/kot` | Generate KOT | JWT | industry + role | Yes |
| GET | `/api/v1/restaurant/kitchen` | Kitchen queue | JWT | industry + role | Yes |
| POST | `/api/v1/wastage` | Record food wastage (deducts stock) | JWT | `wastage.write` | Yes |
| GET | `/api/v1/wastage` | List wastage entries | JWT | `wastage.read` | Yes |
| GET | `/api/v1/reports/fb` | F&B sales by channel/table | JWT | `reports` | Yes |
| GET/POST | `/api/v1/restaurant/recipes` | Recipe CRUD | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
