# User Manual — Business Billing

**Product:** Business Billing  
**Provider:** Prabha Technology Pvt. Ltd.  
**Plan:** Published prices come from Master Admin plans (landing page). In-app there is **no Pay / checkout** — contact support to activate or renew.

## What it is

Cloud billing for **any** shop type: restaurant, hotel, clothing, grocery, pharmacy-style retail, and more. Each registered business is an isolated **tenant**.

## Roles

| Role | Focus |
|------|--------|
| **Owner** | Catalog policy, users, reports, AI, audit, settings, and billing |
| **Billing User** | Day-to-day counter billing, items, and bill history |
| **Master Admin** | Prabha Technology only — registration approval, plans, trials, business lifecycle. Not a shop login. |

## Getting started

1. Open the public site → **Register Business** (accept Terms and Privacy Policy).  
2. Wait for Prabha Technology to **approve** the request. You cannot sign in while status is pending.  
3. After approval email, sign in at **Login** (`/login`) — Owners land on the Owner Dashboard; Billing Users on Billing.  
4. If a trial is enabled, billing works until the trial end date. If trial is off, wait for your plan to be assigned.  
5. Optional: switch **Light / Dark** mode (saved on this device).

Master operators do **not** use `/login` for administration. They use the unadvertised `/master/login` path (footer dot on the landing page). See [master-admin-manual.md](./master-admin-manual.md).

**QA sample business:** Shree General Store (Grocery) — Owner `owner@example.com`, Billing `billing@example.com`. Exact catalog and bill steps: [test-business-billing-guide.md](./test-business-billing-guide.md). New SaaS registration sample: Shree Family Restaurant (`rahul.test@example.com`) in the same guide.

## Common workflows

| Goal | Where |
|------|--------|
| Create a sale | Billing → **New Bill** |
| Review today’s bills | Billing → Bills (or Owner → Bills) |
| Manage catalog | Items / Categories |
| Sales performance | Owner → Sales Reports |
| Insights | Owner → AI Assistant |
| Business profile, WhatsApp & plan | Owner → Settings |
| Change password | Account menu → Change Password |

## Bill basics

- Search items → add to cart → adjust qty (qty ≤ 0 removes line) → optional discount  
- Set **Reference** (table / token / counter note — not hotel-only)  
- Optional customer mobile for WhatsApp delivery  
- Choose **Cash** or **Online**  
- Generate → **Print Bill** and/or **Send on WhatsApp** (independent)  
- Cancel finalized bills with a reason (history retained)

## Support

- Email: prabha.technology.01@gmail.com  
- Phone: 8767865572  
- Address: B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune, Maharashtra – 411041  


## Related manuals

- [Owner Manual](./owner-manual.md)  
- [Billing User Manual](./billing-user-manual.md)  
- [Master Admin Manual](./master-admin-manual.md)  
- [Privacy Policy](./privacy-policy.md) · [Terms of Service](./terms-of-service.md)  
