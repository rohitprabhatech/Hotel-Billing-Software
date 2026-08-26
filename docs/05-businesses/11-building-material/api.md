# Building Material — API

Shared document APIs (module-gated; also used by hardware / wholesale):

| Method | Endpoint | Purpose | Auth | Permission | Module |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/quotations` | List / create quotations | JWT | billing | `quotation` |
| GET | `/api/v1/quotations/{id}` | Quotation detail | JWT | billing | `quotation` |
| PATCH | `/api/v1/quotations/{id}/status` | DRAFT→SENT / CANCELLED | JWT | billing (owner/manager) | `quotation` |
| POST | `/api/v1/quotations/{id}/convert` | Convert quote → bill | JWT | billing (owner/manager) | `quotation` |
| GET/POST | `/api/v1/challans` | List / create delivery challans | JWT | billing | `delivery_challan` |
| GET | `/api/v1/challans/{id}` | Challan detail | JWT | billing | `delivery_challan` |
| PATCH | `/api/v1/challans/{id}/status` | Dispatch / deliver / cancel | JWT | billing (owner/manager) | `delivery_challan` |
| POST | `/api/v1/challans/{id}/convert` | Convert challan → bill | JWT | billing (owner/manager) | `delivery_challan` |
| GET | `/api/v1/challans/{id}/pdf` | Download challan PDF | JWT | billing | `delivery_challan` |

Numbering: `QT-#####`, `DC-#####` per tenant.

### Trade credit & transport (BIZ-37)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/bills` | Accepts `transport_charge` (module `transport_charges`; post-GST / non-GST) |
| POST | `/api/v1/challans` | Accepts `transport_charge`; convert carries it onto the bill |
| GET | `/api/v1/customers/outstanding` | Customer outstanding (shared ledger) |
| GET/POST | `/api/v1/suppliers/outstanding`, `/suppliers/{id}/ledger`, `/suppliers/{id}/payments` | Supplier outstanding |
| POST | `/api/v1/purchases` | `payment_method=credit` posts supplier ledger |

### Warehouses (BIZ-38)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `/api/v1/warehouses` | List / create locations |
| PATCH | `/api/v1/warehouses/{id}` | Update / set default |
| GET | `/api/v1/warehouses/stocks` | Per-warehouse balances |
| GET/POST | `/api/v1/stock-transfers` | List / create transfers (`ST-#####`) |
| POST | `/api/v1/bills` | Optional `warehouse_id` — sell from that location |

Later pack endpoints (advanced warehouse policies) remain planned.
