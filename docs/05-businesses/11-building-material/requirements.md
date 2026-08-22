# Hardware / Building Material — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| BLDM-REQ-011 | The system shall support: **Multiple units**. | P0 | Industry | Pack entities |
| BLDM-REQ-012 | The system shall support: **Weight / length / area**. | P0 | Industry | Pack entities |
| BLDM-REQ-013 | The system shall support: **Bulk pricing**. | P0 | Industry | Pack entities |
| BLDM-REQ-014 | The system shall support: **Quotation**. | P0 | Industry | Pack entities |
| BLDM-REQ-015 | The system shall support: **Delivery challan**. | P0 | Industry | Pack entities |
| BLDM-REQ-001 | Owner can configure Hardware / Building Material-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| BLDM-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| BLDM-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| BLDM-REQ-004 | System shall support industry features: Multiple units, Weight / length / area, Bulk pricing. | P0 | Industry pack | Feature flags |
| BLDM-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| BLDM-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| BLDM-REQ-007 | Dashboard shows Hardware / Building Material-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| BLDM-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| BLDM-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| BLDM-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
