# Report APIs

Owner / Manager + `reports` permission.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/reports/available` | Module-filtered report registry (BIZ-61) |
| GET | `/api/v1/reports/summary` | Dashboard period summary |
| GET | `/api/v1/reports/daily-sales` | Daily sales (+ `page`/`per_page` for bills) |
| GET | `/api/v1/reports/weekly-sales` | Weekly sales |
| GET | `/api/v1/reports/monthly-sales` | Monthly sales |
| GET | `/api/v1/reports/custom-sales` | Custom range (max 366 days) |
| GET | `/api/v1/reports/fb` | F&B channel/table/wastage (`order_channels`) |
| GET | `/api/v1/reports/outstanding` | Aged outstanding (`customer_credit` industries) |
| GET | `/api/v1/reports/export` | xlsx / csv / pdf export |

Industry metrics may also expose scoped routes (`/grocery/sales`, `/clothing/sales`, `/mobile/sales`, `/commissions/report`) — listed via `/reports/available`.
