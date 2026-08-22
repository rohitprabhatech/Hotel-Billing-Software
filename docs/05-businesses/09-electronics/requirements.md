# Electronics Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| ELEC-REQ-011 | The system shall support: **Serial number**. | P0 | Industry | Pack entities |
| ELEC-REQ-012 | The system shall support: **Warranty tracking**. | P0 | Industry | Pack entities |
| ELEC-REQ-013 | The system shall support: **Product model / brand**. | P0 | Industry | Pack entities |
| ELEC-REQ-014 | The system shall support: **Barcode**. | P0 | Industry | Pack entities |
| ELEC-REQ-015 | The system shall support: **Exchange / Return**. | P0 | Industry | Pack entities |
| ELEC-REQ-001 | Owner can configure Electronics Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| ELEC-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| ELEC-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| ELEC-REQ-004 | System shall support industry features: Serial number, Warranty tracking, Product model / brand. | P0 | Industry pack | Feature flags |
| ELEC-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| ELEC-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| ELEC-REQ-007 | Dashboard shows Electronics Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| ELEC-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| ELEC-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| ELEC-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
