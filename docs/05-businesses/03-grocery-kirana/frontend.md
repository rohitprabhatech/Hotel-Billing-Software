# Grocery Stores / Kirana — Frontend

## Fast POS (BIZ-20)

| Route | Page | Module gate | Purpose |
|-------|------|-------------|---------|
| `/billing/grocery` | `GroceryPosPage` | `barcode_pos` | Billing-user scan-first POS |
| `/owner/grocery` | `GroceryPosPage` | `barcode_pos` | Owner/manager scan-first POS |

**UX:** Barcode field auto-focused; Enter scans. Weight UoMs (`kg`, `g`, `l`, `ml`) allow decimal qty with 0.001 step. Cart merges repeated scans of the same item. Checkout calls common `POST /bills` (cash default).

**Services:** `frontend/src/services/groceryService.js` → `GET /grocery/pos-catalog`; barcode lookup reuses `getItemByBarcode`.

## Bulk pricing (BIZ-21)

| UI | Module gate | Purpose |
|----|-------------|---------|
| Items page → “Bulk price tiers” icon | `bulk_pricing` | Owner/staff with `items.write` edit min-qty → unit-price table |
| Grocery POS cart | `barcode_pos` (+ tiers when `bulk_pricing`) | Line unit price updates as qty crosses tiers; bill server re-resolves |
| `/owner/batches` Batches / Expiry | `batch_expiry` | Receive dated batches, expiry report, adjust with required reason |

## Credit / udhari (BIZ-23)

| UI | Module gate | Purpose |
|----|-------------|---------|
| Grocery POS cart | `customer_credit` | Customer picker, cash/online/credit toggle, confirm dialog on udhari |
| `/owner/credit`, `/billing/credit` | `customer_credit` | Outstanding list, collect payment, ledger history |
| Sales Reports → Kirana tab | `barcode_pos` | Daily sales mix + outstanding totals |

**Services:** `frontend/src/services/groceryService.js` — outstanding, credit ledger, pay, sales.

## Other conceptual routes

| Page | Purpose | Roles | Components | API deps | UX |
|------|---------|-------|------------|----------|-----|
| Grocery Dashboard | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Products / Units | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Customers / Credit | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Suppliers / Purchase (common) | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Expiry / Low Stock | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Reports | Grocery Stores / Kirana ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |

## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
