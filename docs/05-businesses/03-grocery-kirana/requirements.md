# Grocery Stores / Kirana — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| GROC-REQ-011 | The system shall support: **Barcode scanner flow**. | P0 | Industry | Pack entities |
| GROC-REQ-012 | The system shall support: **Unit management (kg, g, L, piece)**. | P0 | Industry | Pack entities |
| GROC-REQ-013 | The system shall support: **Low-stock alerts**. | P0 | Industry | Pack entities |
| GROC-REQ-014 | The system shall support: **Stock adjustment**. | P0 | Industry | Pack entities |
| GROC-REQ-015 | The system shall support: **Customer credit / Udhari**. | P0 | Industry | Pack entities |
| GROC-REQ-001 | Owner can configure Grocery Stores / Kirana-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| GROC-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| GROC-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| GROC-REQ-004 | System shall support industry features: Barcode scanner flow, Unit management (kg, g, L, piece), Low-stock alerts. | P0 | Industry pack | Feature flags |
| GROC-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| GROC-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| GROC-REQ-007 | Dashboard shows Grocery Stores / Kirana-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| GROC-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| GROC-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| GROC-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
