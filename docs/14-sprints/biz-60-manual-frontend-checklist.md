# BIZ-60 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`). Set `business_type = travel_agency`.

## Navigation & modules

- [ ] Owner sees **Tour Packages**, **Travel Bookings**, **Travel Agents**
- [ ] Wholesale warehouses, serial/IMEI, tables/kitchen, furniture board are **hidden**

## Tour packages (BIZ-56)

- [ ] Create package with code, destination, duration, price
- [ ] **Create bill** from package card; inventory stock for linked item stays untracked / null
- [ ] Billing can list + bill; cannot create/edit packages

## Bookings & payments (BIZ-57)

- [ ] Create booking with advance; board shows remaining due
- [ ] Confirm → In progress → Complete only after balance is zero
- [ ] Notifications: payment due / booking confirmed appear for owner
- [ ] Billing can create booking + record payment; cannot change status

## Itinerary & documents (BIZ-58)

- [ ] Booking **Details**: add hotel / vehicle / ticket lines; delete works
- [ ] Documents tab: add passport/visa/ID metadata (no file upload required)
- [ ] Billing can view details; cannot add itinerary or documents

## Agents & commission (BIZ-59)

- [ ] Create agent with default commission %
- [ ] New booking with agent shows commission on card / detail
- [ ] Agents page: commission report totals; mark entry paid
- [ ] Billing can view report; cannot create agents

## Cross-check

- [ ] Restaurant tenant does not see travel-only nav
- [ ] Second tenant cannot open first tenant’s booking documents (API 404)

## Responsive smoke

- [ ] Booking board usable at ~375px
- [ ] Details dialog tabs usable on narrow screens
- [ ] Commission report table scrolls horizontally on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
