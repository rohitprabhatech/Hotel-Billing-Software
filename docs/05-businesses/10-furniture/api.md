# Furniture Shops — API

Product attributes (BIZ-47) live on common `/items`. Custom orders (BIZ-48) reuse shared `/custom-orders` with `order_type=furniture`.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST/PUT | `/api/v1/items` (+ `/:id`) | Catalog L/W/H, material, color | JWT | items read/write | Yes |
| GET | `/api/v1/items?q=` | Search includes material / color | JWT | items:read | Yes |
| GET/POST | `/api/v1/custom-orders` | Shared custom orders (`order_type=furniture`) | JWT | billing + `custom_orders` | Yes |
| PATCH | `/api/v1/custom-orders/{id}/status` | Status pipeline (Owner/Manager) | JWT | billing | Yes |
| POST | `/api/v1/custom-orders/{id}/advance` | Additional advance | JWT | billing | Yes |
| GET/POST | `/api/v1/furniture/custom-orders` | Furniture alias (forces type) | JWT | billing + `custom_orders` | Yes |
| POST | `/api/v1/furniture/custom-orders/{id}/advance` | Advance alias | JWT | billing | Yes |
| GET/POST | `/api/v1/deliveries` | Delivery jobs for ready furniture orders | JWT | billing + `delivery_tracking` | Yes |
| PATCH | `/api/v1/deliveries/{id}/status` | SCHEDULED → OUT_FOR_DELIVERY → DELIVERED | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/furniture/deliveries` | Furniture delivery aliases | JWT | as above | Yes |
| POST | `/api/v1/furniture/installations` | Install from `custom_order_id` (furniture) | JWT | billing + `installation` | Yes |
| GET/POST | `/api/v1/furniture/quotations` | Furniture quotation aliases | JWT | billing + `quotation` | Yes |
| POST | `/api/v1/furniture/quotations/{id}/convert` | Convert QT → bill | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/quotations` | Shared quotations | JWT | billing + `quotation` | Yes |

Field mapping on custom orders: `size` = dimensions text, `flavor` = material, `notes` = finish/extras, `delivery_at` = delivery slot.

## Contract notes

- Create advance must be **&lt; total**; later advances up to remaining.
- Status: BOOKED → CONFIRMED → IN_PRODUCTION → READY → (delivery job) → DELIVERED.
- Direct PATCH to DELIVERED on furniture orders returns 400 when `delivery_tracking` is enabled.
- Billing cannot change status.
- **Errors:** 401 / 403 / 404 / 400.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
