# BIZ-39 Manual Frontend Smoke Checklist

Use after the automated pytest gate passes. Switch the tenant business type as noted. Fixture: **Hotel A** (`owner@hotela.com` / `Owner@12345`).

## Hardware (`business_type = hardware`)

### Navigation & modules

- [ ] Owner sees Hardware POS, Quotations, Challans, Credit
- [ ] Warehouses nav is **hidden**
- [ ] Restaurant/cafe nav (Tables, Kitchen) is **hidden**

### Measurement POS

- [ ] Hardware POS catalog loads; units include length/area options
- [ ] Quote for pipe 10 × ₹450 shows line total ₹4,500
- [ ] Item form shows stock UoM vs sale UoM when measurement module is on

### Quotations & challans

- [ ] Create quotation; convert to bill; QT number visible
- [ ] Create challan with transport charge; PDF downloads; convert carries transport
- [ ] Billing user can list quotations but cannot create

### Credit & transport

- [ ] New Bill / Hardware POS accepts transport charge
- [ ] Credit sale posts to customer outstanding on Credit page
- [ ] Supplier tab: credit purchase appears; record supplier payment

## Building Material (`business_type = building_material`)

- [ ] Same quotes / challans / credit / transport as hardware
- [ ] **Warehouses** nav visible; default MAIN present
- [ ] Create second warehouse; transfer stock; balances update
- [ ] Bill can sell from selected warehouse; stock decreases there only
- [ ] Hardware POS may be less central; New Bill still works with UoM / transport

## Responsive smoke

- [ ] Hardware POS usable at ~375px
- [ ] Quotations / Challans forms usable on mobile
- [ ] Warehouses transfer dialog usable on narrow screens
- [ ] Credit Customer | Supplier tabs wrap without covering actions

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | Owner | | |
| | Manager | | |
| | Billing | | |
