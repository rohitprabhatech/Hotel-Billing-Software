# Common Module — Billing

**Single reusable billing engine** for all industries.

## Supports

Products · Services · Mixed invoices · Qty/Unit/Price · Discount · CGST/SGST/IGST · Cash/Online/UPI/Card/Credit · Partial/Advance · Returns/Refunds (target) · Print/PDF/WhatsApp

## Industry packs

Document only **extensions** (e.g. KOT→bill, IMEI line, service booking line). Do not fork a second engine.

## Current baseline

`bills` / `bill_items` with cash|online, cancel, PDF, WhatsApp/email exist today.

## Stock rule

Product lines: reject insufficient stock unless setting allows negative. Concurrent-safe checks required.
