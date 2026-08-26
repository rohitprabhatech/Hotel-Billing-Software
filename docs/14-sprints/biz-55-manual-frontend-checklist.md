# BIZ-55 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`). Set `business_type = wholesale`.

## Navigation & modules

- [ ] Owner sees **Price Lists**, **Sales Orders**, **Purchase Orders**, **Warehouses**, **Delivery Challans**, **Credit / Udhari**, **Outstanding Report**, **Quotations**, barcode/Grocery POS
- [ ] Furniture Orders, Deliveries board, Serial/IMEI, Cake Orders, Tables/Kitchen are **hidden**

## Price lists (BIZ-51)

- [ ] Create default wholesale list; set item prices
- [ ] Assign customer to a VIP list
- [ ] New Bill / POS: walk-in vs assigned customer shows different unit prices
- [ ] Billing can view lists but cannot create

## Sales / purchase orders (BIZ-52)

- [ ] Create SO → Confirm → Convert to bill; stock decreases
- [ ] Create PO → Confirm → Convert to purchase; stock increases
- [ ] Billing can list SO/PO; Owner/Manager write and convert

## Warehouses (BIZ-53)

- [ ] Default MAIN warehouse appears; create second location
- [ ] Transfer stock; balances move; item total unchanged
- [ ] POS / New Bill: sell-from warehouse picker; stock deducts from selected WH
- [ ] Transfer dialog shows available qty at **from** warehouse

## Outstanding & invoice (BIZ-54)

- [ ] Outstanding Report shows aged buckets; print works
- [ ] Credit sale appears under customer outstanding; pay reduces balance
- [ ] Bill PDF shows **TAX INVOICE** when GST applies
- [ ] Create delivery challan; download PDF

## Cross-check

- [ ] Restaurant tenant does not see wholesale-only nav

## Responsive smoke

- [ ] Price Lists usable at ~375px
- [ ] SO / PO dialogs usable on narrow screens
- [ ] Outstanding table scrolls horizontally on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
