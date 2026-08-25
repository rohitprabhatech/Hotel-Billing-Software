# Clothing Shops — Frontend

Reuse common Items, New Bill, Reports. Industry nav appears when `variants` / `product_images` are enabled.

| Page | Purpose | Roles | Components | API deps |
|------|---------|-------|------------|----------|
| Clothing POS (`/owner/clothing`, `/billing/clothing`) | Size×color stock grid + thumbnails | Billing + Owner | VariantStockGrid, product cards | `GET /clothing/pos-catalog`, `POST /bills` |
| Returns (`/owner/returns`, `/billing/returns`) | Wizard: find bill → qty → return or exchange | Owner / Manager (Billing view-only) | Stepper | `/returns` |
| Variants (`/owner/variants`) | Tenant-wide size/color stock list | Owner / Manager | Table + item filter | `GET /item-variants` |
| Items matrix | Per-item variant editor | Owner / Manager | Dialog grid | `PUT /items/:id/variants` |
| Items images | URL or file gallery | Owner / Manager | Thumbnails | `/items/:id/images` |
| New Bill | Size/color stock grid before add | Billing + Owner | VariantStockGrid | `GET /items/:id/variants` |
| Reports — Apparel | Brand/size/color/category filters + variant stock | Owner / Manager | Tabs on Reports | `GET /clothing/sales` |
| Customers — history | Bills with variant line names | Staff with customers.read | History dialog | `GET /clothing/customer-history` |

## Shared UI

Reuse common Billing, Customers, Reports pages.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
