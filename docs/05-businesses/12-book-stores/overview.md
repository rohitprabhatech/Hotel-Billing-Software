# Book Stores — Overview

**Business code:** `bookstore`  
**Documentation pack:** `docs/05-businesses/12-book-stores/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Book Stores tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Publisher/author catalog, barcode

| Aspect | Detail |
|--------|--------|
| Billing type | Product POS with ISBN metadata |
| Inventory | ISBN/title stock, returns, bulk pricing |

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

- ISBN
- Author / Publisher / Edition
- Barcode
- Book category
- Stock management
- Bulk pricing
- Customer purchase history
- Return management

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
