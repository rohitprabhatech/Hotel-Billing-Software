# Business Types — Prabha Billing SaaS V2

**Count:** Exactly **14**  
**Excluded:** Medical Stores (and all medical-specific entities)

---

## Canonical list

| # | Display name | Suggested code | Nature |
|---|--------------|----------------|--------|
| 1 | Hotels / Restaurants | `hotel_restaurant` | Product + service (F&B) |
| 2 | Cafes / Tea Shops | `cafe_tea` | Product + quick service |
| 3 | Grocery Stores / Kirana | `grocery_kirana` | Product / POS |
| 4 | Clothing Shops | `clothing` | Product + variants |
| 5 | Mobile Shops | `mobile` | Product + serial/IMEI |
| 6 | Hardware Stores | `hardware` | Product + units |
| 7 | Bakery / Sweet Shops | `bakery_sweets` | Product + batch/orders |
| 8 | Stationery Shops | `stationery` | Product / POS |
| 9 | Electronics Shops | `electronics` | Product + serial/warranty |
| 10 | Furniture Shops | `furniture` | Product + custom orders |
| 11 | Hardware / Building Material | `building_material` | Product + measure/units |
| 12 | Book Stores | `bookstore` | Product + ISBN |
| 13 | Wholesale Shops | `wholesale` | Product + B2B |
| 14 | Travel Agencies | `travel_agency` | **Service-first** |

> **Migration note:** Current codes (`restaurant`, `hotel`, `kirana_store`, …) must map to this list in a future sprint. Mapping table is a development task — **not** executed in this phase.

---

## Activation chain

```
Business registers
  → selects Business Type
    → Industry Configuration
      → Enabled Modules
        → Enabled Features
          → Navigation + Dashboard widgets
```

Do not scatter `if (businessType === …)` across unrelated files. Prefer a **configuration registry** resolved at login / bootstrap.

---

## Module enablement (summary)

| Type | Billing | Inventory | Tables/KOT | Variants | Serial/IMEI | Batch/Expiry | Credit | Travel booking |
|------|---------|-----------|------------|----------|-------------|--------------|--------|----------------|
| Hotel/Restaurant | ✓ | ✓ (+recipe) | ✓ | — | — | optional | optional | — |
| Cafe/Tea | ✓ | ✓ | optional | — | — | optional | — | — |
| Grocery/Kirana | ✓ | ✓ | — | — | — | ✓ | ✓ | — |
| Clothing | ✓ | ✓ | — | size/color | — | — | — | — |
| Mobile | ✓ | ✓ | — | — | ✓ | — | — | — |
| Hardware | ✓ | ✓ | — | units | — | — | ✓ | — |
| Bakery | ✓ | ✓ | — | — | — | ✓ | — | — |
| Stationery | ✓ | ✓ | — | — | — | — | ✓ | — |
| Electronics | ✓ | ✓ | — | — | ✓ | — | — | — |
| Furniture | ✓ | ✓ | — | dims | — | — | — | — |
| Building material | ✓ | ✓ | — | measure | — | — | ✓ | — |
| Books | ✓ | ✓ | — | ISBN | — | — | — | — |
| Wholesale | ✓ | ✓ | — | warehouses | — | — | ✓ | — |
| Travel | ✓ (service) | light/none | — | — | — | — | — | ✓ |

---

## Medical Store — permanent exclusion

Do **not** include in:

- UI dropdowns, landing industry grid, docs, APIs, DB design, tests, manuals, sprint tasks  
- Entities: Medicine, Prescription, Medicine Batch, Medical Returns, Medical Dashboard  

Generic **batch / lot / expiry** remain for Grocery, Bakery, etc.

---

## Travel vs product billing

Travel Agencies are **service-management** businesses: packages, bookings, advances, itineraries, commissions. Inventory is optional/light. Documented in [billing-engine.md](./billing-engine.md) and [industry-modules.md](./industry-modules.md).
