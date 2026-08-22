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
- Customer credit / Udhari
- Customer payment history
- Bulk pricing
- Expiry tracking (generic inventory)
- Fast POS billing (BIZ-20: `/billing/grocery`, `/owner/grocery`, module `barcode_pos`)

## Explicitly NOT enabled (examples)

Features belonging to other industries stay **off** via configuration (see feature matrix).  
**Medical Store / medicine / prescription features are never enabled.**
