# Grocery Stores / Kirana — Workflow

## Primary flow

```
Customer
  → Product Selection (scan/search)
  → Cart
  → Billing
  → Payment (cash / credit)
  → Invoice
  → Stock Deduction
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
