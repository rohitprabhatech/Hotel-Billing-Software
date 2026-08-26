# BIZ-34 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Switch the tenant business type as noted. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`).

## Mobile (`business_type = mobile`)

### Navigation & modules

- [ ] Owner sees Serial / IMEI, Returns, Repairs, Mobile tab on Reports
- [ ] Installations nav is **hidden**
- [ ] Restaurant/cafe nav (Tables, Kitchen) is **hidden**

### Catalog & POS

- [ ] Item form shows Brand, Model, Track serial, Warranty months
- [ ] New Bill requires picking an in-stock IMEI for serial items
- [ ] Receipt / PDF shows IMEI and warranty until date when set

### Serial / IMEI page

- [ ] Receive unit; duplicate IMEI rejected
- [ ] Quarantine chip appears after a quarantined return

### Returns

- [ ] Lookup shows IMEI on serial lines
- [ ] Return can quarantine; exchange picks a replacement IMEI
- [ ] Billing user cannot confirm return/exchange

### Repairs

- [ ] Create ticket from board; advance Received → In progress → Ready → Delivered
- [ ] Ready creates an in-app notification

### Reports & customers

- [ ] Mobile report shows by brand / model and IMEI stock
- [ ] Customer purchase history shows IMEI (and warranty if present)

## Electronics (`business_type = electronics`)

- [ ] Same serial / warranty / returns / repairs / Mobile report as mobile
- [ ] **Installations** nav visible
- [ ] Schedule install against a sold serial; Upcoming-by-date list + status columns work
- [ ] Manager can schedule/update install; billing user can view only

## Responsive smoke

- [ ] Serial receive dialog usable at ~375px
- [ ] Returns wizard usable on mobile
- [ ] Repair / Installation boards scroll columns on narrow screens
- [ ] Reports Mobile tab filters wrap without covering Generate

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
