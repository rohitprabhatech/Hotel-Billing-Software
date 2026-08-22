# Furniture Shops — Overview

**Business code:** `furniture`  
**Documentation pack:** `docs/05-businesses/10-furniture/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Furniture Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Dimensions, custom work, delivery/install

| Aspect | Detail |
|--------|--------|
| Billing type | Showroom sales + custom orders with advances |
| Inventory | Finished goods + materials; delivery/install jobs |

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

- Product dimensions / material / color
- Custom furniture orders
- Advance / remaining payment
- Delivery management
- Installation tracking
- Order status
- Customer quotation

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
