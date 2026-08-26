# Stationery Shops — Frontend

Routes (BIZ-44):

| Page | Path | Roles | Notes |
|------|------|-------|-------|
| Stationery POS | `/owner/stationery`, `/billing/stationery` | Owner / Manager / Billing | Search-first + barcode + credit checkout |
| Credit | `/owner/credit`, `/billing/credit` | Owner / Manager / Billing | Shared grocery credit UI (`customer_credit`) |
| Items / Customers / Bills / Reports | common paths | As permitted | Shared |

## Shared UI

- Nav item **Stationery POS** appears only when `business_type === 'stationery'` and module `barcode_pos` is on.
- **Grocery POS** is hidden for stationery tenants (`hideForBusinessTypes`).
- Service: `frontend/src/services/stationeryService.js`
- Page: `frontend/src/pages/modules/StationeryPosPage.jsx`

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
