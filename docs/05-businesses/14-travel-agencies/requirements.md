# Travel Agencies — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| TRVL-REQ-011 | The system shall support: **Tour package management**. | P0 | Industry | Pack entities |
| TRVL-REQ-012 | The system shall support: **Package pricing**. | P0 | Industry | Pack entities |
| TRVL-REQ-013 | The system shall support: **Booking management**. | P0 | Industry | Pack entities |
| TRVL-REQ-014 | The system shall support: **Advance / remaining payment**. | P0 | Industry | Pack entities |
| TRVL-REQ-015 | The system shall support: **Booking status**. | P0 | Industry | Pack entities |
| TRVL-REQ-001 | Owner can configure Travel Agencies-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| TRVL-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| TRVL-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| TRVL-REQ-004 | System shall support industry features: Tour package management, Package pricing, Booking management. | P0 | Industry pack | Feature flags |
| TRVL-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| TRVL-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| TRVL-REQ-007 | Dashboard shows Travel Agencies-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| TRVL-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| TRVL-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| TRVL-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
