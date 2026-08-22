# Plan Management — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Operator UI:** Master → Plans  
**Public API:** `GET /api/v1/public/plans`

---

## Catalog fields

| Field | Notes |
|-------|--------|
| name, description | Shown on landing cards |
| price | INR, ≥ 0, stored DECIMAL |
| billing_cycle | `MONTHLY` or `YEARLY` |
| features | List of strings (e.g. Billing, Stock, Reports, AI Insights, WhatsApp) |
| trial_eligible | Informational for operators |
| is_public | Must be true to appear on the landing page |
| is_active | Inactive plans cannot be assigned to **new** subscriptions |
| display_order | Landing sort |

---

## Landing page

The pricing section loads **active + public** plans from the API, ordered by `display_order`. Deactivate a plan to hide it. Create “Professional / ₹999 / Monthly” and it appears without a frontend code change.

---

## Price changes vs existing businesses

Editing a plan price does **not** rewrite `subscriptions.price_at_purchase`. Historical billed amounts stay on the subscription row.

Assign or renew snapshots the **current** catalog price at that moment.

---

## Deactivate vs delete

Plans are not hard-deleted from the Master UI. Set `is_active=false`. Existing subscriptions keep `plan_id` (FK ON DELETE SET NULL only if a plan row were removed at the database layer — the app does not do that).

Related: [subscription-management.md](./subscription-management.md) · [master-admin-manual.md](./master-admin-manual.md)
