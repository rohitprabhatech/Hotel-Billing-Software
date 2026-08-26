# Wholesale Shops — Frontend

| Page | Path | Roles | Notes |
|------|------|-------|-------|
| Price Lists | `/owner/price-lists` | Owner / Manager / Billing (read) | Matrices + customer assignments (`price_lists`) |
| Sales Orders | `/owner/sales-orders` | Owner / Manager / Billing (read) | SO → bill (`sales_orders`) |
| Purchase Orders | `/owner/purchase-orders` | Owner / Manager / Billing (read) | PO → purchase (`purchase_orders`) |
| Grocery / Barcode POS | `/owner/grocery` | Owner / Manager / Billing | List prices when customer selected |
| Quotations | shared `/owner/quotations` | As permitted | Module `quotation` |
| Delivery Challans | `/owner/challans` | Owner / Manager / Billing | Module `delivery_challan`; PDF |
| Credit / Udhari | `/owner/credit` | Owner / Manager | Collections + ledger |
| Outstanding Report | `/owner/outstanding` | Owner / Manager | Aged buckets + print |
| Warehouses | `/owner/warehouses` | Owner / Manager / Billing (read) | Sell-from on POS & New Bill; transfer UX |

## UX (BIZ-51 … BIZ-54)

- Create wholesale lists; mark one as default; assign customers
- POS cart recalculates when customer changes
- Create SO / PO documents; confirm; convert to bill or purchase
- Pick sell-from warehouse on barcode POS and New Bill; transfer shows available at source
- Aged outstanding report with print; tax invoice PDF on bills with GST

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
