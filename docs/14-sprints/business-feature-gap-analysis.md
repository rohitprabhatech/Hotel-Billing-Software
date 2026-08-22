# Business Feature Gap Analysis

**Product:** Prabha Billing SaaS  
**Date:** 2026-08-20  
**Method:** Code inspection (`backend/app`, `frontend/src`) + existing docs — **not guesswork**.  
**Scope:** Planning only. No code or database changes.

**Legend:** Existing = in application code · Partial = some support · Missing = docs-only / absent  
**DB / API / FE** = expected change if we implement the feature later.

---

## 0. Common platform (applies to all 14 businesses)

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Authentication / JWT | YES | | | No | No | No |
| Tenant isolation (server `tenant_id`) | YES | | | No | No | No |
| Business registration + Master approval | YES | | | No | No | No |
| Subscription / free trial / Master Admin | YES | | | No | No | No |
| Owner + Billing User roles | YES | | | No | No | No |
| Manager role | | | YES | Maybe (role seed) | YES | YES |
| Categories + Products/Items | YES | | | Extend later | Extend | Extend |
| Billing + GST + PDF + print | YES | | | Extend | Extend | Extend |
| Stock qty + movements + oversell block | YES | | | Extend | Extend | Extend |
| Sales reports | YES | | | Extend | Extend | Extend |
| Notifications + audit (tenant + platform) | YES | | | Extend | Extend | Extend |
| WhatsApp + email bill delivery | YES | | | No | No | No |
| AI sales assistant | YES | | | No | Extend | Extend |
| Dark mode + responsive MUI shell | YES | | | No | No | Extend pages |
| Customer master (CRM) | | PARTIAL (bill fields only) | | YES | YES | YES |
| Supplier master | | | YES | YES | YES | YES |
| Purchases module | | PARTIAL (receive-stock) | | YES | YES | YES |
| Expenses module | | | YES | YES | YES | YES |
| Business type catalog (14 types) | | PARTIAL (9 codes in code) | | Data domain | YES | YES |
| Feature / module configuration flags | | | YES | YES | YES | YES |
| Barcode field + UoM engine | | PARTIAL (SKU search) | | YES | YES | YES |
| Party credit / udhari ledger | | | YES | YES | YES | YES |
| Returns / exchange framework | | PARTIAL (bill cancel) | | YES | YES | YES |
| Serial / IMEI units | | | YES | YES | YES | YES |
| Dining tables / KOT / kitchen | | PARTIAL (`bills.table_number` text) | | YES | YES | YES |
| Warehouses / multi-location stock | | | YES | YES | YES | YES |
| Quotations / delivery challans | | | YES | YES | YES | YES |
| Travel bookings / packages | | | YES | YES | YES | YES |

**Stock safety today:** When `item.stock_quantity` is set, `bill_service` locks the row, rejects oversell, deducts stock, writes `stock_movements`. Unlimited stock if quantity is `NULL`. Industry models must keep this invariant.

**Medical Store:** Permanently excluded — not in code; must not appear in catalogs or sprints as a product vertical.

---

## 1. Hotels / Restaurants

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Menu / products | YES | | | Extend | Extend | Extend |
| Table management + status | | PARTIAL (text ref) | | YES | YES | YES |
| Dine-in / takeaway / delivery orders | | | YES | YES | YES | YES |
| KOT + kitchen dashboard | | | YES | YES | YES | YES |
| Waiter management | | | YES | YES | YES | YES |
| Split bill / merge tables | | | YES | YES | YES | YES |
| Discount / service charge | | PARTIAL (discount possible ad-hoc) | | YES | YES | YES |
| Recipe / ingredient stock | | | YES | YES | YES | YES |
| Food wastage | | | YES | YES | YES | YES |
| Billing / invoice / payments / reports | YES | | | Extend | Extend | Extend |
| Customers / purchase / expenses | | PARTIAL / Missing (common) | | YES | YES | YES |

**Workflow gap:** Table → Order → KOT → Kitchen → Bill → Pay → Invoice → Inventory → Report is **not** implemented end-to-end (only Bill → Pay → Invoice → Stock → Report).

---

## 2. Cafes / Tea Shops

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Quick / takeaway billing | YES | | | No | No | YES (UX) |
| Menu | YES | | | Extend | Extend | Extend |
| KOT / tables | | | YES | YES (shared w/ restaurant) | YES | YES |
| Add-ons / combos / coupons | | | YES | YES | YES | YES |
| Ingredient stock | | | YES | YES (shared recipes) | YES | YES |
| Popular item report | | PARTIAL (sales reports) | | Maybe | YES | YES |

---

## 3. Grocery / Kirana

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Product + billing + inventory | YES | | | Extend | Extend | YES (fast POS) |
| Barcode | | PARTIAL (SKU) | | YES | YES | YES |
| Units kg/g/l/pcs | | | YES | YES | YES | YES |
| Low-stock alert | YES | | | No | No | No |
| Stock adjustment | YES | | | Extend (reasons/batches) | Extend | Extend |
| Customer credit / udhari | | | YES | YES | YES | YES |
| Bulk pricing | | | YES | YES | YES | YES |
| Expiry / batch | | | YES | YES | YES | YES |
| Suppliers / purchases / expenses | | / Missing | | YES | YES | YES |

---

## 4. Clothing

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Product / billing / inventory | YES | | | Extend | Extend | Extend |
| Size / color / brand variants | | | YES | YES | YES | YES |
| Size/color-wise stock | | | YES | YES | YES | YES |
| Barcode / SKU / images | | PARTIAL (SKU) | | YES | YES | YES |
| Exchange / return | | PARTIAL (cancel) | | YES | YES | YES |
| Sales by brand + purchase history | | PARTIAL (reports; no CRM) | | YES | YES | YES |

---

## 5. Mobile Shops

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Product / billing / inventory | YES | | | Extend | Extend | Extend |
| IMEI / serial stock | | | YES | YES | YES | YES |
| Model / brand / warranty | | | YES | YES | YES | YES |
| Accessories | | PARTIAL (as separate items) | | Maybe | Maybe | YES |
| Exchange / repair tracking | | | YES | YES | YES | YES |
| Customer history | | PARTIAL | | YES (CRM) | YES | YES |

---

## 6. Hardware Stores

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core retail loop | YES | | | Extend | Extend | Extend |
| Weight / length / bulk qty | | | YES | YES | YES | YES |
| Variants / brand | | | YES | YES | YES | YES |
| Customer / supplier credit | | | YES | YES | YES | YES |
| Price history | | | YES | YES | YES | YES |

---

## 7. Bakery / Sweet Shops

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core billing / inventory | YES | | | Extend | Extend | Extend |
| Production runs | | | YES | YES | YES | YES |
| Ingredient inventory / recipes | | | YES | YES | YES | YES |
| Batch / expiry / wastage | | | YES | YES | YES | YES |
| Custom cake orders + advance | | | YES | YES | YES | YES |

---

## 8. Stationery

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core POS loop | YES | | | Minimal | Minimal | YES (pack UX) |
| Barcode / bulk / credit / low stock | | PARTIAL | | Shared modules | Shared | Shared |
| Fast search POS | | PARTIAL | | No | No | YES |

---

## 9. Electronics

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core loop | YES | | | Extend | Extend | Extend |
| Serial / warranty / brand / model | | | YES | Shared w/ mobile | YES | YES |
| Exchange / return / repair | | | YES | Shared | YES | YES |
| Installation tracking | | | YES | YES | YES | YES |

---

## 10. Furniture

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core loop | YES | | | Extend | Extend | Extend |
| Dimensions / material / color | | | YES | YES | YES | YES |
| Custom orders + advance/remaining | | | YES | YES (share custom orders) | YES | YES |
| Delivery / installation / quotation | | | YES | YES | YES | YES |

---

## 11. Hardware / Building Material

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core loop | YES | | | Extend | Extend | Extend |
| Multi-unit / area / bulk | | | YES | Shared UoM | YES | YES |
| Quotation / challan / transport | | | YES | YES | YES | YES |
| Credit + warehouse stock | | | YES | YES | YES | YES |
| Price history | | | YES | YES | YES | YES |

---

## 12. Book Stores

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core loop | YES | | | Extend | Extend | Extend |
| ISBN / author / publisher / edition | | | YES | YES | YES | YES |
| Bulk pricing / barcode / returns | | PARTIAL | | Shared | Shared | Shared |
| Customer history | | PARTIAL | | CRM | YES | YES |

---

## 13. Wholesale

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Core loop + GST invoice | YES | | | Extend | Extend | Extend |
| Wholesale / retail / customer pricing | | | YES | YES | YES | YES |
| Credit + outstanding reports | | | YES | YES | YES | YES |
| Multi-warehouse + transfer | | | YES | YES | YES | YES |
| PO / SO / quotation / challan | | | YES | YES | YES | YES |

---

## 14. Travel Agencies

| Feature | Existing? | Partial? | Missing? | Database Change? | API Change? | Frontend Change? |
|---|---|---|---|---|---|---|
| Customers / billing / payments / expenses / invoice | | PARTIAL (billing yes; CRM/expenses missing) | | YES | YES | YES |
| Tour packages | | | YES | YES | YES | YES |
| Bookings + advance/remaining + status | | | YES | YES | YES | YES |
| Hotel / vehicle / ticket / itinerary / documents | | | YES | YES | YES | YES |
| Agent commission | | | YES | YES | YES | YES |
| Classic inventory deduction | N/A (service) | | | Avoid forcing stock | Special path | YES |

---

## Evidence anchors (code)

| Area | Path |
|---|---|
| Business types (9 codes) | `backend/app/constants/business_types.py` |
| Bills + stock check | `backend/app/services/bill_service.py` |
| Items / stock | `backend/app/models/item.py`, `stock_movement.py` |
| Master / subscriptions | `backend/app/routes/master_routes.py` |
| Frontend routes | `frontend/src/routes/paths.js` |
| No customers/tables/KOT/IMEI models | `backend/app/models/` (23 tables) |

---

## Planning implication

1. **Do not rebuild** auth, tenancy, Master Admin, core billing, stock lock, WhatsApp, AI, audit.  
2. **Phase 01** must close common CRM/procurement/config gaps before industry packs.  
3. **Prefer shared modules** (tables/KOT, serials, variants, credit, UoM, warehouses, quotes, custom orders).  
4. Implementation sprints: see `sprint-biz-01` … `sprint-biz-68` and `sprint-tracker.md`.
