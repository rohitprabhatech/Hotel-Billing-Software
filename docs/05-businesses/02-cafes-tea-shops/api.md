# Cafes / Tea Shops — API

Namespace: `/api/v1/cafe/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/cafe/pos-catalog` | Menu + add-on groups + combos for quick POS | JWT | `addons.read` | Yes |
| GET/POST | `/api/v1/menu/addons` | Add-on group catalog / create | JWT | `addons.read` / `addons.write` | Yes |
| DELETE | `/api/v1/menu/addons/:id` | Remove add-on group | JWT | `addons.write` | Yes |
| GET/POST | `/api/v1/combos` | Combo offers | JWT | `addons.read` / `addons.write` | Yes |
| GET/DELETE | `/api/v1/combos/:id` | Combo detail / delete | JWT | `addons.read` / `addons.write` | Yes |

Orders accept `addon_ids` on line items and `combos[]` on create when the `addons_combos` module is enabled (cafe tenants only). Use `POST /api/v1/orders/:id/settle` for quick bill flow.

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
