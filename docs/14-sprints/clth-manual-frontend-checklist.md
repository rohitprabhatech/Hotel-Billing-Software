# CLTH Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`) with business type **Clothing Shops** (Owner → Settings).

Also test **Billing** (`billing@hotela.com` / `Billing@12345`) and **Cafe regression** (`owner@hotelb.com` on cafe tenant).

## CLTH-1 — Nav & isolation

- [ ] Owner Sell section: **Clothing POS** emphasized; no Tables / Kitchen / Cafe POS
- [ ] Billing drawer: short nav (POS, bills, returns, catalog) — no Reports
- [ ] Drawer subtitle: **Clothing Billing**
- [ ] Cafe tenant (`owner@hotelb.com`): no Clothing POS bleed

## CLTH-2 — Billing home

- [ ] `/billing` shows **Clothing Billing** hero + Clothing POS card
- [ ] KPIs: today's sales, bills, out-of-stock variant count
- [ ] Quick links: POS, Returns, today's bills table

## CLTH-3 — Barcode POS

- [ ] Scan field visible when `barcode_pos` module on
- [ ] Variant barcode adds correct size/color to cart
- [ ] Item-only barcode opens size/color picker

## CLTH-4 — Owner dashboard

- [ ] Period selector (Last 7 Days, etc.)
- [ ] KPIs: Returns count, Low Variants
- [ ] Top Sizes Sold / Top Colors Sold tables
- [ ] Low Variant Stock alert + table
- [ ] Returns & Exchanges section

## CLTH-5 — POS polish

- [ ] Category chips filter product grid
- [ ] Customer picker on cart; credit requires customer
- [ ] Post-bill dialog: Print, PDF, WhatsApp
- [ ] Mobile (~375px): sticky bottom bar, 2-column grid, qty +/−

## BIZ-28 baseline (unchanged)

- [ ] Variants + images on Items
- [ ] Returns / exchange restock correct variant
- [ ] Apparel tab on Reports matches sales
- [ ] Customer purchase history shows size/color

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | | | |
