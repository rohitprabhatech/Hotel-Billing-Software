# Grocery Stores / Kirana — Frontend

## Fast POS (BIZ-20)

| Route | Page | Module gate | Purpose |
|-------|------|-------------|---------|
| `/billing/grocery` | `GroceryPosPage` | `barcode_pos` | Billing-user scan-first POS |
| `/owner/grocery` | `GroceryPosPage` | `barcode_pos` | Owner/manager scan-first POS |

**UX:** Barcode field auto-focused; Enter scans. Weight UoMs (`kg`, `g`, `l`, `ml`) allow decimal qty with 0.001 step. Cart merges repeated scans of the same item. Checkout calls common `POST /bills` (cash default).

**Services:** `frontend/src/services/groceryService.js` → `GET /grocery/pos-catalog`; barcode lookup reuses `getItemByBarcode`.

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
