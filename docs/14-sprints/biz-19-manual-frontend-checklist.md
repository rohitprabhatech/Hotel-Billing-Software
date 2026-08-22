# BIZ-19 Manual Frontend Smoke Checklist

Use after automated pytest gate passes. Test as **Owner**, **Manager**, and **Billing user** where noted.

Fixture tenants: **Hotel A** (`owner@hotela.com`) = restaurant; **Hotel B** (`owner@hotelb.com`) = cafe.

## Navigation & modules

- [ ] Restaurant owner sees Tables, Menu, Orders, Kitchen, Recipes, Wastage
- [ ] Cafe owner sees Cafe POS, add-ons/combos modules (no Recipes-only restaurant extras if disabled)
- [ ] Billing user sees Orders + Kitchen; does **not** see Wastage or Recipes (owner nav)
- [ ] Clothing business type hides F&B nav items

## Tables (`/owner/tables`, `/billing/tables`)

- [ ] Table board loads with status chips
- [ ] Create table (owner)
- [ ] Billing user can mark occupied / available (not create tables)
- [ ] Merge / unmerge tables (owner)

## Orders (`/owner/orders`, `/billing/orders`)

- [ ] New order — dine-in requires table; takeaway works without
- [ ] Add lines, cancel open order
- [ ] Settle order dialog — discount, service charge, payment method
- [ ] Split bill from orders page (where exposed)

## Kitchen (`/owner/kitchen`, `/billing/kitchen`)

- [ ] Kitchen queue shows fired KOTs
- [ ] Status transitions: queued → preparing → ready
- [ ] Print KOT page opens

## Cafe POS (`/billing/cafe`, `/owner/cafe`) — cafe tenant only

- [ ] Popular combos chips visible
- [ ] Add-on picker on menu item tap
- [ ] Quick bill creates order + settled bill

## Recipes & wastage (owner)

- [ ] Recipes page — link menu item to ingredients
- [ ] Wastage page — log loss; stock decreases on item detail

## Reports (`/owner/reports`)

- [ ] Sales tab — daily report generates
- [ ] **F&B Insights** tab — channel chart, table table, wastage summary

## Responsive smoke (optional)

- [ ] Kitchen board usable at ~375px width (cards stack, actions reachable)
- [ ] Cafe POS cart column stacks below menu grid on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | | | |
