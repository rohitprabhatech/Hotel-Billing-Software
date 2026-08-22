# Hotels / Restaurants — Workflow

## Primary flow

```
Customer
  → Table Selection
  → **Order** (dine-in / takeaway / delivery — BIZ-13)
  → KOT
  → Kitchen
  → Food Preparation
  → Billing
  → Payment
  → Invoice
  → Stock / Recipe Deduction
  → Sales Report
```

## Notes

- Tenant isolation applies at every step.
- Product stock movements use the **common inventory engine** when lines are PRODUCT.
- Service-oriented steps (especially Travel) may skip stock deduction.
- Payments/invoices reuse the **common billing engine**.

## Mermaid

```mermaid
flowchart TD
  A[Start] --> B[Industry entry steps]
  B --> C[Common Billing]
  C --> D[Payment]
  D --> E[Invoice / PDF / WhatsApp]
  E --> F[Inventory if product]
  F --> G[Reports / Audit]
```
