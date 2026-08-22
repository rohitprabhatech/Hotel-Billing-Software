# Bakery / Sweet Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| BAKE-REQ-011 | The system shall support: **Product production**. | P0 | Industry | Pack entities |
| BAKE-REQ-012 | The system shall support: **Ingredient inventory**. | P0 | Industry | Pack entities |
| BAKE-REQ-013 | The system shall support: **Batch management**. | P0 | Industry | Pack entities |
| BAKE-REQ-014 | The system shall support: **Expiry tracking**. | P0 | Industry | Pack entities |
| BAKE-REQ-015 | The system shall support: **Custom cake orders (size/flavor)**. | P0 | Industry | Pack entities |
| BAKE-REQ-001 | Owner can configure Bakery / Sweet Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| BAKE-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| BAKE-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| BAKE-REQ-004 | System shall support industry features: Product production, Ingredient inventory, Batch management. | P0 | Industry pack | Feature flags |
| BAKE-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| BAKE-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| BAKE-REQ-007 | Dashboard shows Bakery / Sweet Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| BAKE-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| BAKE-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| BAKE-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
