# BIZ-28 Manual Frontend Smoke Checklist

Use after automated pytest gate passes. Switch the tenant to **Clothing Shops** first (Settings → business type), then test as **Owner**, **Manager**, and **Billing user** where noted.

Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`) after `business_type = clothing`.

## Navigation & modules

- [ ] Owner sees Clothing POS, Variants, Returns, Apparel tab on Reports
- [ ] Restaurant/cafe nav (Tables, Kitchen, Cafe POS) is **hidden**
- [ ] Grocery Credit / Udhari and Batches are **hidden**
- [ ] Billing user sees Clothing POS + Returns (view); does **not** see Sales Reports

## Clothing POS (`/owner/clothing`, `/billing/clothing`)

- [ ] Size×color grid shows stock; empty cell cannot be billed
- [ ] Thumbnail shows when a primary image exists
- [ ] Cash bill deducts only the selected variant

## Variants & images (`/owner/items`, `/owner/variants`)

- [ ] Size+color row unique; first variant may inherit parent stock
- [ ] Image URL or file upload (≤2 MB) appears in the gallery

## Returns (`/owner/returns`)

- [ ] Lookup by bill number lists returnable qty
- [ ] Return restocks the original size/color
- [ ] Exchange requires a different variant; billing user cannot POST

## Reports (`/owner/reports`) — Apparel tab

- [ ] Brand / size / color / category tables match a known sale
- [ ] Brand filter narrows rows
- [ ] Returns KPI increments after a return
- [ ] Variant stock table lists current sizes

## Customers

- [ ] Purchase history shows item names including size/color

## Responsive smoke — required for this gate

- [ ] Clothing POS usable at ~375px: grid, cart, Bill button reachable
- [ ] Apparel report filters wrap without covering Generate
- [ ] Returns wizard usable on mobile

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | | | |
