# Billing Engine — Prabha Billing SaaS V2

## Goal

**One** reusable billing engine for all industries. Industry packs extend line metadata and workflows; they do not fork a second engine unless an approved exception exists.

## Line types

| Type | Use |
|------|-----|
| PRODUCT | Physical / stocked goods |
| SERVICE | Travel packages, repairs, installation, fees |
| MIXED | Same invoice may contain both |

## Capabilities

- Quantity, unit, unit price  
- Discount (line / bill)  
- Tax: GST with CGST / SGST / IGST modes  
- Service charge (restaurant) as configurable line/fee  
- Payments: cash, online, UPI, card, credit, partial, advance  
- Returns / refunds  
- Print, PDF, WhatsApp/email send  
- Snapshots on lines so catalog edits don’t rewrite history  

## Stock interaction

On finalize of PRODUCT lines:

1. Lock / check available quantity (variant/serial/batch aware).  
2. Reject if insufficient unless `allow_negative_stock`.  
3. Write stock movements.  
4. Handle concurrency (two cashiers).  

SERVICE lines skip stock unless linked to serialized goods.

## Travel difference

Travel invoices primarily SERVICE (packages/bookings). Advances and balances tracked via payments. Optional merchandise PRODUCT lines allowed.

## Current baseline

`bills` + `bill_items` with cash/online, cancel, PDF, WhatsApp/email. Extend toward payments table, returns, UPI/card/credit, product/service split.
