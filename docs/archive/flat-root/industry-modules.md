# Industry Modules — Prabha Billing SaaS V2

Each module pack enables **only** industry-specific workflows on top of Common Core.  
**Medical Store:** not defined and must never be added under this program without a new approved product decision.

---

## Shared pattern

```
Industry Pack
  ├── Feature flags (from BusinessType config)
  ├── Entities (conceptual — see database-architecture.md)
  ├── APIs under /api/v1/{industry}/...
  ├── UI pages under modules/{industry}/
  └── Dashboard widgets
```

---

## 1. Hotels / Restaurants

**Core:** Menu/products, tables, dine-in / takeaway / delivery, KOT, billing, invoice, customers, inventory, purchase, expenses, daily sales, GST, payments.  
**Special:** Table status Available/Occupied/Reserved; kitchen dashboard; waiter; split bill; merge tables; discount; service charge; food wastage; recipe stock.  
**Workflow:** Table → Order → KOT → Kitchen → Prep → Billing → Payment → Invoice → Inventory deduction → Sales report.  
**Dashboard:** Today’s sales, tables, orders, KOT, kitchen, top food, low stock, pending payments.

## 2. Cafes / Tea Shops

**Core:** Menu, quick/takeaway billing, customers, inventory, expenses, reports.  
**Special:** Optional KOT/tables; add-ons; combos; coupons; popular-item report; ingredient stock.  
**Dashboard:** Today’s sales, popular items, low stock, takeaway queue.

## 3. Grocery / Kirana

**Core:** Products, billing, customers, suppliers, purchase, inventory, expenses, reports.  
**Special:** Barcode; units kg/g/L/piece; low stock; stock adjust; customer credit (udhari); payment history; bulk pricing; expiry; fast POS.  
**Dashboard:** Today’s sales, fast movers, low stock, credit, purchase, expenses.

## 4. Clothing Shops

**Core:** Products, billing, customers, suppliers, inventory, purchase, reports.  
**Special:** Size S–XXL; color; brand; barcode; SKU; images; size/color stock; exchange/return; brand/category sales; purchase history.  
**Dashboard:** Today’s sales, top brands/categories, size/color stock, low stock.

## 5. Mobile Shops

**Core:** Products, billing, inventory, customers, suppliers, purchase, reports.  
**Special:** IMEI/serial; model; brand; warranty; accessories; exchange; repair/service; IMEI stock.  
**Dashboard:** Today’s sales, IMEI stock, warranty, accessories, low stock.

## 6. Hardware Stores

**Core:** Products, billing, inventory, purchase, suppliers, customers, reports.  
**Special:** Units; weight/length; bulk; brand; variants; low stock; customer/supplier credit; price history.  
**Example:** 10 pipes × ₹450 = ₹4,500.  
**Dashboard:** Sales, low stock, credit, top SKUs.

## 7. Bakery / Sweet Shops

**Core:** Products, billing, inventory, customers, purchase, expenses, reports.  
**Special:** Production; ingredients; batch; expiry; custom cake (size/flavor); advance; delivery datetime; order status; wastage.  
**Dashboard:** Sales, production, custom orders due, low ingredients, wastage.

## 8. Stationery Shops

**Core:** Products, billing, inventory, purchase, suppliers, customers, reports.  
**Special:** Barcode; SKU; brand; category; bulk pricing; low stock; credit; fast POS; search.  
**Dashboard:** Sales, low stock, top categories.

## 9. Electronics Shops

**Core:** Products, billing, inventory, purchase, suppliers, customers, reports.  
**Special:** Serial; warranty; model; brand; barcode; exchange/return; repair; installation; history.  
**Dashboard:** Sales, serial stock, warranty due, low stock.

## 10. Furniture Shops

**Core:** Products, billing, customers, inventory, purchase, expenses, reports.  
**Special:** Dimensions; material; color; custom orders; advance/balance; delivery/install; quotation; status.  
**Dashboard:** Sales, custom orders, deliveries, pending balances.

## 11. Hardware / Building Material

**Core:** Products, billing, inventory, purchase, supplier, customer, reports.  
**Special:** Multi-unit; weight/length/area; bulk; quotation; delivery challan; credit; transport; warehouse; price history.  
**Dashboard:** Sales, warehouse stock, credit, quotations.

## 12. Book Stores

**Core:** Products, billing, inventory, purchase, suppliers, customers, reports.  
**Special:** ISBN; author; publisher; edition; barcode; category; bulk; history; returns.  
**Dashboard:** Sales, top titles, low stock.

## 13. Wholesale Shops

**Core:** Products, billing, inventory, purchase, customers, suppliers, expenses, reports.  
**Special:** Wholesale/retail/customer pricing; bulk; credit; outstanding; multi-warehouse; stock transfer; PO/SO; quotation; challan; barcode; GST.  
**Dashboard:** Sales, outstanding, top customers/products, warehouse stock.

## 14. Travel Agencies

**Core:** Customers, billing, payments, expenses, reports, invoices.  
**Special:** Travel details; packages; bookings; advance/balance; status; hotel/vehicle/tickets; documents; itinerary; agent commission.  
**Billing difference:** Service/package lines dominate; physical stock usually off. Mixed invoices allowed if selling merchandise.  
**Dashboard:** Bookings today, revenue, pending payments, upcoming trips, popular packages, commission.

---

## Implementation order (see sprint-plan.md)

Restaurant/Cafe → Grocery/Retail → Clothing/Mobile → Hardware/Building → Bakery/Stationery/Electronics → Furniture/Books/Wholesale → Travel.
