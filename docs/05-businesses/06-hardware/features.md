# Hardware Stores — Features

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

- Unit management (pcs, kg, m, ft, sqm, sqft, …)
- Length / weight / area selling with decimal quantities (BIZ-35)
- Separate stock UoM vs sale UoM (`items.sale_uom`)
- Hardware POS with live line quote
- Customer quotations convertible to bills (BIZ-36)
- Delivery challans with PDF print (BIZ-36)
- Bulk quantity / tiers (when `bulk_pricing` on)
- Brand management
- Product variants
- Low-stock alerts
- Customer / supplier credit
- Price history (planned later sprints)

## Explicitly NOT enabled (examples)

Features belonging to other industries stay **off** via configuration (see feature matrix).  
**Medical Store / medicine / prescription features are never enabled.**
