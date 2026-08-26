# Wholesale Shops — Reports

## Industry reports

- **Aged outstanding** (customers + suppliers): 0–30 / 31–60 / 61–90 / 90+ via FIFO on open credit charges — `GET /api/v1/reports/outstanding`
- Warehouse stock (balances + transfers)
- Wholesale / customer-wise sales (shared sales reports)
- Top products (shared sales reports)

## Common reports reused

- Today's / weekly / monthly sales  
- Payment report  
- GST totals on sales reports  
- Bill PDF as **TAX INVOICE** when GST / wholesale / GSTIN  

See [`../../04-common-modules/reports.md`](../../04-common-modules/reports.md).

## UI

- `/owner/outstanding` — Outstanding Report (print-friendly)
- `/owner/credit` — collect / ledger
- `/owner/reports` — period sales
