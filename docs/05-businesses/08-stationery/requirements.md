# Stationery Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| STAT-REQ-011 | The system shall support: **Barcode / SKU**. | P0 | Industry | Pack entities |
| STAT-REQ-012 | The system shall support: **Brand management**. | P0 | Industry | Pack entities |
| STAT-REQ-013 | The system shall support: **Category management**. | P0 | Industry | Pack entities |
| STAT-REQ-014 | The system shall support: **Bulk pricing**. | P0 | Industry | Pack entities |
| STAT-REQ-015 | The system shall support: **Low-stock alerts**. | P0 | Industry | Pack entities |
| STAT-REQ-001 | Owner can configure Stationery Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| STAT-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| STAT-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| STAT-REQ-004 | System shall support industry features: Barcode / SKU, Brand management, Category management. | P0 | Industry pack | Feature flags |
| STAT-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| STAT-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| STAT-REQ-007 | Dashboard shows Stationery Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| STAT-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| STAT-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| STAT-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
