# BIZ-24 Manual Frontend Smoke Checklist

Use after automated pytest gate passes. Switch the tenant to **Grocery / Kirana** first (Settings → business type), then test as **Owner**, **Manager**, and **Billing user** where noted.

Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`) after `business_type = grocery_kirana`.

## Navigation & modules

- [ ] Owner sees Grocery POS, Credit / Udhari, Batches / Expiry
- [ ] Restaurant/cafe nav (Tables, Kitchen, Cafe POS) is **hidden**
- [ ] Billing user sees Grocery POS + Credit / Udhari; does **not** see Sales Reports
- [ ] Clothing business type keeps barcode POS, hides Credit / Udhari and Batches

## Grocery POS (`/owner/grocery`, `/billing/grocery`)

- [ ] Scan field auto-focused; Enter adds a line
- [ ] Weight item (kg) allows decimal qty (e.g. 0.750)
- [ ] Repeated scan of the same barcode merges quantity
- [ ] Customer picker + **Credit (Udhari)** only after a customer is selected
- [ ] Confirm dialog appears before posting udhari
- [ ] Cash bill still works without a customer
- [ ] Insufficient stock shows an error and does not empty the cart incorrectly

## Credit / Udhari (`/owner/credit`, `/billing/credit`)

- [ ] Outstanding list shows warning chips
- [ ] Collect → Review → Confirm reduces balance
- [ ] Payment history dialog lists CREDIT_SALE / PAYMENT

## Batches / Expiry (`/owner/batches`)

- [ ] Receive batch requires expiry date
- [ ] Expiry report shows expired vs expiring
- [ ] Adjust batch requires a reason

## Items — bulk pricing

- [ ] Bulk price tiers editor (when `bulk_pricing` on)
- [ ] POS line rate updates when qty crosses a tier

## Reports (`/owner/reports`)

- [ ] Sales tab — Credit filter + Credit Sales KPI
- [ ] **Kirana** tab — daily mix + outstanding totals

## Notifications

- [ ] Credit sale creates a dues notification
- [ ] Near-expiry batch receive can notify
- [ ] Low stock after a bill that crosses minimum

## Responsive smoke (POS mobile) — required for this gate

- [ ] Grocery POS usable at ~375px: scan field, cart table/scroll, Bill button reachable
- [ ] Credit confirm dialog fits viewport
- [ ] Credit / Udhari collect dialog usable on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | | | |
