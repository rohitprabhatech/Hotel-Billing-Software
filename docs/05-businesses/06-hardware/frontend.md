# Hardware Stores — Frontend

| Page | Route | Roles | Notes |
|------|-------|-------|-------|
| Hardware POS | `/owner/hardware`, `/billing/hardware` | Owner / Manager / Billing | Decimal qty by sale UoM; quote preview; checkout via `/bills` |
| Items | `/owner/items` | Owner / Manager | Stock unit + optional sale unit when `uom_measurement` enabled |

## Shared UI

Reuse common Billing, Customers, Reports. Hardware POS nav appears when module `uom_measurement` is enabled.
