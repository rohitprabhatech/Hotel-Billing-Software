# Cafes / Tea Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| CAFE-REQ-011 | The system shall support: **Optional Tables / KOT**. | P0 | Industry | Pack entities |
| CAFE-REQ-012 | The system shall support: **Add-ons**. | P0 | Industry | Pack entities |
| CAFE-REQ-013 | The system shall support: **Combo offers**. | P0 | Industry | Pack entities |
| CAFE-REQ-014 | The system shall support: **Discount / coupon**. | P0 | Industry | Pack entities |
| CAFE-REQ-015 | The system shall support: **Popular-item report**. | P0 | Industry | Pack entities |
| CAFE-REQ-001 | Owner can configure Cafes / Tea Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| CAFE-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| CAFE-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| CAFE-REQ-004 | System shall support industry features: Optional Tables / KOT, Add-ons, Combo offers. | P0 | Industry pack | Feature flags |
| CAFE-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| CAFE-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| CAFE-REQ-007 | Dashboard shows Cafes / Tea Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| CAFE-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| CAFE-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| CAFE-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
