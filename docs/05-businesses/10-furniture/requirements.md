# Furniture Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| FURN-REQ-011 | The system shall support: **Product dimensions / material / color**. | P0 | Industry | Pack entities |
| FURN-REQ-012 | The system shall support: **Custom furniture orders**. | P0 | Industry | Pack entities |
| FURN-REQ-013 | The system shall support: **Advance / remaining payment**. | P0 | Industry | Pack entities |
| FURN-REQ-014 | The system shall support: **Delivery management**. | P0 | Industry | Pack entities |
| FURN-REQ-015 | The system shall support: **Installation tracking**. | P0 | Industry | Pack entities |
| FURN-REQ-001 | Owner can configure Furniture Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| FURN-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| FURN-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| FURN-REQ-004 | System shall support industry features: Product dimensions / material / color, Custom furniture orders, Advance / remaining payment. | P0 | Industry pack | Feature flags |
| FURN-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| FURN-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| FURN-REQ-007 | Dashboard shows Furniture Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| FURN-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| FURN-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| FURN-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
