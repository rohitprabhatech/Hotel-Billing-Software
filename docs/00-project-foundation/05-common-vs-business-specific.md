# Common vs Industry Features

## What is common across all businesses?

| Area | Examples |
|------|----------|
| Platform | Auth, tenant, Master Admin, registration, subscription, trial |
| Commerce | Billing engine, payments, invoices, print/PDF, WhatsApp send |
| Catalog | Categories, products/services (shape varies) |
| Parties | Customers (and suppliers where enabled) |
| Ops | Notifications, audit, settings, reports shell, AI (optional) |
| Inventory kernel | Quantity modes, movements, low-stock (when product-based) |

## What changes by business type?

| Industry | Examples of what changes |
|----------|--------------------------|
| Restaurant | Tables, KOT, kitchen, recipes, wastage |
| Cafe | Add-ons, combos, optional KOT |
| Grocery | Barcode, units, credit/udhari, expiry |
| Clothing | Size, color, brand, variants, exchange |
| Mobile | IMEI, warranty, repair |
| Hardware | UOM, bulk, price history, credit |
| Bakery | Batches, cake orders, production wastage |
| Stationery | Fast search POS, brands, bulk price |
| Electronics | Serial, warranty, install, repair |
| Furniture | Specs, quotes, custom orders, delivery |
| Building material | Warehouses, challans, transport, measure |
| Books | ISBN metadata, returns |
| Wholesale | Price lists, PO/SO, warehouses, outstanding |
| Travel | Packages, bookings, itinerary, commission (service-first) |

## Configuration idea (pre-implementation)

```
BusinessType → enabled Modules/Features → Navigation + API allow-list + Dashboard widgets
```

Restaurant: Billing=YES, Tables=YES, KOT=YES, IMEI=NO, Travel Booking=NO  
Clothing: Billing=YES, Size/Color=YES, KOT=NO  
Travel: Billing=YES (service), Inventory=LIGHT/NO, Packages=YES

See [business-feature-matrix.md](./business-feature-matrix.md).
