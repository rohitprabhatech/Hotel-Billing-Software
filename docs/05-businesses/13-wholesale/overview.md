# Wholesale Shops — Overview

**Business code:** `wholesale`  
**Documentation pack:** `docs/05-businesses/13-wholesale/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Wholesale Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Credit, PO/SO, quotations, challans, outstanding

| Aspect | Detail |
|--------|--------|
| Billing type | B2B wholesale/retail/customer-wise pricing |
| Inventory | Multi-warehouse, transfers, bulk qty |

## Typical workflow

See [workflow.md](./workflow.md).

## Common modules reused

- Authentication
- Authorization
- Billing Engine
- Customers
- Payments
- Inventory (generic)
- Categories / Products
- Reports (common)
- Notifications
- Audit Logs
- Printing / PDF
- WhatsApp (optional)
- AI Assistant (optional)
- Settings

> Billing details live in [`../../04-common-modules/billing.md`](../../04-common-modules/billing.md). This pack only documents **extensions**.

## Industry-specific modules / features

- Wholesale / retail / customer-wise pricing
- Bulk quantity
- Credit / Udhari
- Payment tracking
- Outstanding reports
- Multiple warehouses
- Stock transfer
- Purchase order / Sales order
- Quotation / Delivery challan
- Barcode
- GST invoice

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
