# Clothing Shops — Reports

## Industry reports

`GET /api/v1/clothing/sales` (Owner/Manager, module `variants`, permission `reports`).

- Sales by brand (Unbranded when the line has no variant brand)
- Sales by size
- Sales by color
- Sales by category
- Current variant stock snapshot
- Returns / exchange counts and refund totals for the period

Filters: date or from/to, payment method, brand, size, color, category.

Customer history with size/color line names: `GET /api/v1/clothing/customer-history?customer_id=` (also shown on Customers → Purchase History when `variants` is on).

## Common reports reused

- Today's / weekly / monthly sales  
- Payment report  
- GST report (where applicable)  

See [`../../04-common-modules/reports.md`](../../04-common-modules/reports.md).
