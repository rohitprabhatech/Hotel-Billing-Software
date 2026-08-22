# Hotels / Restaurants — Overview

**Business code:** `hotel_restaurant`  
**Documentation pack:** `docs/05-businesses/01-hotels-restaurants/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Hotels / Restaurants tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User; future Waiter / Kitchen User

## Business characteristics

Table-driven service, kitchen production, GST F&B billing

| Aspect | Detail |
|--------|--------|
| Billing type | Product (menu) + optional service charge; dine-in / takeaway / delivery |
| Inventory | Finished menu items + optional recipe/ingredient stock |

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

- Table Management (Available / Occupied / Reserved)
- KOT
- Kitchen Dashboard
- Waiter Management
- Split Bill
- Merge Tables
- Recipes / Ingredient Stock
- Food Wastage
- Service Charge

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
