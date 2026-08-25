# Clothing Shops — Features

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

- **Size / color / brand variants (BIZ-25)** — independent stock, SKU, barcode per combination
- **Product images (BIZ-26)** — URL metadata or local upload; POS thumbnails
- **Clothing POS (BIZ-26)** — size×color stock picker; cannot sell an empty cell
- **Returns / exchange (BIZ-27)** — restock original variant; optional swap into another size/color
- Exchange / Return (BIZ-27)
- **Sales by brand / size / color / category (BIZ-28)** — Apparel tab on Reports
- **Customer purchase history (BIZ-28)** — variant line names on Customers history

## Explicitly NOT enabled (examples)

Features belonging to other industries stay **off** via configuration (see feature matrix).  
**Medical Store / medicine / prescription features are never enabled.**
