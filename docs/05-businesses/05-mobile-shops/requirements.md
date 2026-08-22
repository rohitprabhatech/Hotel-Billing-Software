# Mobile Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| MOBL-REQ-011 | The system shall support: **IMEI number**. | P0 | Industry | Pack entities |
| MOBL-REQ-012 | The system shall support: **Serial number**. | P0 | Industry | Pack entities |
| MOBL-REQ-013 | The system shall support: **Mobile model / brand**. | P0 | Industry | Pack entities |
| MOBL-REQ-014 | The system shall support: **Warranty tracking**. | P0 | Industry | Pack entities |
| MOBL-REQ-015 | The system shall support: **Accessories management**. | P0 | Industry | Pack entities |
| MOBL-REQ-001 | Owner can configure Mobile Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| MOBL-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| MOBL-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| MOBL-REQ-004 | System shall support industry features: IMEI number, Serial number, Mobile model / brand. | P0 | Industry pack | Feature flags |
| MOBL-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| MOBL-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| MOBL-REQ-007 | Dashboard shows Mobile Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| MOBL-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| MOBL-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| MOBL-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
