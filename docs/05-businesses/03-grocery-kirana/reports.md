# Grocery Stores / Kirana — Reports

## Industry reports

- Daily sales (common reports + grocery `GET /grocery/sales`)
- Fast-moving products (`top_items` on sales / Kirana tab)
- Low stock (common inventory health)
- Expiry / near-expiry (BIZ-22)
- Customer credit outstanding (`GET /grocery/outstanding`, Kirana report `outstanding`)
- Purchase vs sales (common purchases + sales)

Credit mix: `metrics.credit_sales` / `credit_bill_count` on daily sales and dashboard.

## Common reports reused

- Today's / weekly / monthly sales  
- Payment report  
- GST report (where applicable)  

See [`../../04-common-modules/reports.md`](../../04-common-modules/reports.md).
