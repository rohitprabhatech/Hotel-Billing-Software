# BIZ-50 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`). Set `business_type = furniture`.

## Navigation & modules

- [ ] Owner sees **Furniture Orders**, **Deliveries**, **Installations**, **Quotations**
- [ ] Cake Orders, Warehouses, Book fields, Serial/IMEI nav are **hidden**
- [ ] Restaurant/cafe nav (Tables, Kitchen) is **hidden**

## Items (BIZ-47)

- [ ] Items form shows dimensions, material, color
- [ ] Search finds item by material or color
- [ ] Cash bill deducts stock

## Furniture orders (BIZ-48)

- [ ] Book custom piece with dimensions, material, advance &lt; total
- [ ] Status board: Booked → … → Ready
- [ ] No “Mark delivered” on Ready when delivery module on; info banner points to Deliveries
- [ ] Billing can create order + record advance; Manager/Owner change status

## Deliveries (BIZ-49)

- [ ] Schedule delivery from ready order; appears on board
- [ ] Out for delivery → Delivered; order moves to Delivered column
- [ ] Billing can view board; Owner/Manager updates status

## Installations (BIZ-49)

- [ ] Schedule installation from ready custom order (no serial picker)
- [ ] Status: Scheduled → In progress → Completed

## Quotations (BIZ-50)

- [ ] Create quotation with furniture catalog lines
- [ ] Convert to bill; QT status CONVERTED
- [ ] Billing can list quotations but cannot create or convert

## Cross-check

- [ ] Restaurant tenant does not see furniture-only nav

## Responsive smoke

- [ ] Furniture Orders kanban usable at ~375px
- [ ] Deliveries board usable on mobile
- [ ] Quotations dialog usable on narrow screens

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
