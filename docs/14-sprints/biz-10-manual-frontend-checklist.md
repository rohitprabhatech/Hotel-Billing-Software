# BIZ-10 Manual Frontend Smoke Checklist

Use after automated pytest gate passes. Test as **Owner** and **Manager** (billing layout) where noted.

## Login & navigation

- [ ] Owner sees Customers, Suppliers, Purchases, Expenses in sidebar
- [ ] Manager sees Purchases, Expenses under billing nav (not Owner dashboard)
- [ ] Billing user does **not** see Purchases or Expenses nav

## Customers (`/owner/customers`, `/billing/customers`)

- [ ] List loads with search
- [ ] Create / edit customer with optional credit limit
- [ ] Balance column shows ₹0 or warning chip when outstanding
- [ ] **Outstanding only** filter shows customers with balance > 0
- [ ] Ledger dialog lists CREDIT_SALE / PAYMENT entries
- [ ] Collect payment dialog reduces balance
- [ ] Purchase history (bills) dialog still works

## Suppliers

- [ ] List + create supplier
- [ ] Billing user can view, not create (read-only actions)

## Purchases (`/owner/purchases`, `/billing/purchases`)

- [ ] List with status filter
- [ ] New purchase — supplier picker, line items, saves and updates stock
- [ ] Cancel finalized purchase (when stock allows reversal)

## Expenses

- [ ] List with from/to date filters
- [ ] Category summary card updates with filters
- [ ] Create / edit / delete expense

## Items & billing

- [ ] Item form — barcode + unit of measure fields save correctly
- [ ] New Bill — barcode scan field adds item on Enter
- [ ] New Bill — **Credit (Udhari)** appears when customer linked; hidden otherwise
- [ ] Credit bill increases customer balance (verify on Customers page)

## Responsive smoke (optional)

- [ ] Customers and New Bill usable at ~375px width (stacked filters, no horizontal overflow on tables)

## Sign-off

| Tester | Role | Date | Pass |
|--------|------|------|------|
| | | | |
