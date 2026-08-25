# Grocery Stores / Kirana — Features

## COMMON FEATURES (reused)

- Billing
- Customer Management
- Payments
- Reports
- Notifications
- Audit
- Printing/PDF
- Settings

Uses: [`../../04-common-modules/billing.md`](../../04-common-modules/billing.md), inventory, customers, etc.

## BUSINESS-SPECIFIC FEATURES

- Barcode scanner flow
- Unit management (kg, g, L, piece)
- Low-stock alerts
- Stock adjustment
- Customer credit / Udhari (BIZ-23: grocery POS credit toggle + `/owner/credit`)
- Customer payment history (BIZ-23: ledger on Credit / Udhari page)
- Bulk pricing (BIZ-21: item price tiers by min qty; POS + bills apply tier)
- Expiry tracking (BIZ-22: optional `tracks_batches`, `/owner/batches`, FEFO block)
- Fast POS billing (BIZ-20: `/billing/grocery`, `/owner/grocery`, module `barcode_pos`)

## Explicitly NOT enabled (examples)

Features belonging to other industries stay **off** via configuration (see feature matrix).  
**Medical Store / medicine / prescription features are never enabled.**
