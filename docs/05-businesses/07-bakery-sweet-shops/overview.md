# Bakery / Sweet Shops — Overview

**Business code:** `bakery_sweets`  
**Documentation pack:** `docs/05-businesses/07-bakery-sweet-shops/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Bakery / Sweet Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Production planning, custom orders, delivery slots

| Aspect | Detail |
|--------|--------|
| Billing type | Retail POS + custom cake orders with advance |
| Inventory | Ingredients, production batches, expiry, wastage |

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

- Product production
- Ingredient inventory
- Batch management
- Expiry tracking
- Custom cake orders (size/flavor)
- Advance / remaining payment
- Delivery date/time
- Order status
- Wastage tracking

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
