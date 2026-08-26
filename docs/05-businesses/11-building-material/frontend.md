# Building Material — Frontend

| Page | Route | Roles | Notes |
|------|-------|-------|-------|
| Quotations | `/owner/quotations` | Owner / Manager (write); Billing read | Quote builder; convert → bill |
| Delivery Challans | `/owner/challans` | Owner / Manager (write); Billing read | Dispatch docs + PDF download |
| Warehouses | `/owner/warehouses` | Owner / Manager (write); Billing read | Locations, balances, transfers |
| Hardware POS | `/owner/hardware`, `/billing/hardware` | Billing+ | Measurement selling (BIZ-35) |

Nav items appear when `quotation` / `delivery_challan` / `warehouse` / `uom_measurement` modules are enabled.
