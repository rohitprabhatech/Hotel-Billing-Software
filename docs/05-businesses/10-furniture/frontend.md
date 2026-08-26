# Furniture Shops — Frontend

| Page | Path | Roles | Notes |
|------|------|-------|-------|
| Furniture catalog (Items) | `/owner/items` | Owner / Manager / Billing | L/W/H + material + color (`furniture_attributes`) |
| Furniture Orders | `/owner/furniture-orders` | Owner / Manager / Billing | Status board + advances (`custom_orders`) |
| Deliveries | `/owner/deliveries` | Owner / Manager / Billing | Last-mile board (`delivery_tracking`) |
| Installations | `/owner/installations` | Owner / Manager / Billing | Serial (electronics) or custom order (furniture) |
| Quotations | `/owner/quotations` | Owner / Manager / Billing | QT-##### create/convert (`quotation`) |

## UX (BIZ-48)

- Kanban: Booked → Confirmed → In production → Ready → Delivered (via Deliveries board)
- Form: title, dimensions (`size`), material (`flavor`), customer, total, advance &lt; total, delivery datetime
- Ready orders: schedule on **Deliveries**; optional **Installations** from ready order
- Cake Orders nav hidden for furniture (`businessTypes` filter)

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
