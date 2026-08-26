# BIZ-43 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Switch tenant to **bakery_sweet**. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`).

## Navigation & modules

- [ ] Owner sees Recipes, Production, Cake Orders, Batches / Expiry, Wastage
- [ ] Serial / IMEI, Warehouses, Tables / Kitchen are **hidden**

## Production

- [ ] Create recipe (FG + ingredients); record production — ingredients down, FG up
- [ ] For batch-tracked FG: expiry required; batch appears on Batches page
- [ ] Billing user cannot create production; Manager can

## Batches / Expiry & wastage

- [ ] Near-expiry / expired report shows bakery FG lots
- [ ] Bill blocks selling more than non-expired sellable qty
- [ ] Wastage can write off expired batch qty; stock and batch qty update

## Cake orders

- [ ] Billing can book cake order with size, flavor, advance < total, delivery datetime
- [ ] Status board columns: Booked → Confirmed → In production → Ready → Delivered
- [ ] Billing cannot change status; Owner/Manager can
- [ ] Record additional advance; remaining due updates
- [ ] Ready creates an in-app notification

## POS

- [ ] New Bill sells baked FG stock (not re-deducting recipe ingredients)

## Responsive smoke

- [ ] Production dialog usable at ~375px
- [ ] Cake Orders board scrolls columns on narrow screens
- [ ] Batches / Wastage forms usable on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
