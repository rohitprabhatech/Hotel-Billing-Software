# Business Feature Matrix

C=COMMON · I=INDUSTRY-SPECIFIC · O=OPTIONAL · N=NOT REQUIRED

| Feature | Restaurant | Cafe | Grocery | Clothing | Mobile | Hardware | Bakery | Stationery | Electronics | Furniture | Building | Books | Wholesale | Travel |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Billing engine | C | C | C | C | C | C | C | C | C | C | C | C | C | C |
| Customers | C | C | C | C | C | C | C | C | C | C | C | C | C | C |
| Inventory qty | C | C | C | C | C | C | C | C | C | C | C | C | C | O |
| Suppliers/Purchase | O | O | C | C | C | C | C | C | C | C | C | C | C | N |
| Expenses | O | O | O | O | O | O | O | O | O | O | O | O | O | O |
| Tables | I | O | N | N | N | N | N | N | N | N | N | N | N | N |
| KOT/Kitchen | I | O | N | N | N | N | N | N | N | N | N | N | N | N |
| Recipes | I | O | N | N | N | N | O | N | N | N | N | N | N | N |
| Barcode POS | O | O | I | I | O | O | O | I | O | N | O | I | I | N |
| Units kg/L/m | O | O | I | N | N | I | O | O | N | O | I | N | I | N |
| Customer credit | O | O | I | O | O | I | O | I | O | O | I | O | I | N |
| Batch/Expiry | O | O | I | N | N | O | I | O | N | N | O | N | O | N |
| Size/Color/Brand | N | N | N | I | O | O | N | O | O | O | N | N | O | N |
| IMEI/Serial | N | N | N | N | I | N | N | N | I | N | N | N | N | N |
| Warranty/Repair | N | N | N | N | I | N | N | N | I | N | N | N | N | N |
| Warehouse/Transfer | N | N | N | N | N | O | N | N | N | O | I | N | I | N |
| Quotation/Challan | N | N | N | N | N | O | N | N | N | I | I | N | I | N |
| Custom orders | N | N | N | N | N | N | I | N | N | I | N | N | N | N |
| Tour packages/Booking | N | N | N | N | N | N | N | N | N | N | N | N | N | I |
| Agent commission | N | N | N | N | N | N | N | N | N | N | N | N | N | I |
| Medical/Prescription | N | N | N | N | N | N | N | N | N | N | N | N | N | N |

Medical/Prescription row is **N** for all types by product decision.
