# Hotels / Restaurants — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| REST-REQ-011 | The system shall support: **Table Management (Available / Occupied / Reserved)**. | P0 | Industry | Pack entities |
| REST-REQ-012 | The system shall support: **KOT**. | P0 | Industry | Pack entities |
| REST-REQ-013 | The system shall support: **Kitchen Dashboard**. | P0 | Industry | Pack entities |
| REST-REQ-014 | The system shall support: **Waiter Management**. | P0 | Industry | Pack entities |
| REST-REQ-015 | The system shall support: **Split Bill**. | P0 | Industry | Pack entities |
| REST-REQ-001 | Owner can configure Hotels / Restaurants-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| REST-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| REST-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| REST-REQ-004 | System shall support industry features: Table Management (Available / Occupied / Reserved), KOT, Kitchen Dashboard. | P0 | Industry pack | Feature flags |
| REST-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| REST-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| REST-REQ-007 | Dashboard shows Hotels / Restaurants-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| REST-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| REST-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| REST-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
