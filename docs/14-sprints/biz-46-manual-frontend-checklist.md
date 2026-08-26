# BIZ-46 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Fixtures: **Hotel A** (`owner@hotela.com` / `Owner@12345`).

## Stationery (`business_type = stationery`)

- [ ] Owner/Billing see **Stationery POS**; Grocery POS is hidden
- [ ] Search by name/SKU/barcode; cash bill updates stock
- [ ] Credit checkout with customer; Credit page shows outstanding
- [ ] Returns nav is **hidden**

## Book store (`business_type = book_store`)

- [ ] Items form shows ISBN / Author / Publisher; search finds by author or ISBN
- [ ] Grocery / barcode POS available; can sell a book
- [ ] Returns nav visible; look up bill → Return → stock back; refund shown
- [ ] Exchange: pick another title from catalog; returned title restocked
- [ ] Billing can list/lookup returns but cannot create; Owner/Manager can

## Cross-check

- [ ] Restaurant tenant does not see stationery/books-only nav or Returns (if not enabled)

## Responsive smoke

- [ ] Stationery POS usable at ~375px
- [ ] Items book fields usable on mobile
- [ ] Returns wizard usable on narrow screens

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
