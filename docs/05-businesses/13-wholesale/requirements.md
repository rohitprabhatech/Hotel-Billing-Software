# Wholesale Shops — Requirements

IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.

| ID | Requirement | Priority | Module | Dependencies |
|----|-------------|----------|--------|--------------|
| WHOL-REQ-011 | The system shall support: **Wholesale / retail / customer-wise pricing**. | P0 | Industry | Pack entities |
| WHOL-REQ-012 | The system shall support: **Bulk quantity**. | P0 | Industry | Pack entities |
| WHOL-REQ-013 | The system shall support: **Credit / Udhari**. | P0 | Industry | Pack entities |
| WHOL-REQ-014 | The system shall support: **Payment tracking**. | P0 | Industry | Pack entities |
| WHOL-REQ-015 | The system shall support: **Outstanding reports**. | P0 | Industry | Pack entities |
| WHOL-REQ-001 | Owner can configure Wholesale Shops-specific catalog/settings for the tenant. | P0 | Settings / Catalog | Common tenant |
| WHOL-REQ-002 | Billing users can create bills using common billing engine with industry line extensions where needed. | P0 | Billing | Common billing |
| WHOL-REQ-003 | System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed). | P0 | Inventory | Common inventory |
| WHOL-REQ-004 | System shall support industry features: Wholesale / retail / customer-wise pricing, Bulk quantity, Credit / Udhari. | P0 | Industry pack | Feature flags |
| WHOL-REQ-005 | All industry data is tenant-scoped; cross-tenant IDs return 403/404. | P0 | Security | AuthZ |
| WHOL-REQ-006 | Owner can view audit/activity for staff billing and catalog actions. | P0 | Audit | Common audit |
| WHOL-REQ-007 | Dashboard shows Wholesale Shops-relevant widgets when business type is enabled. | P1 | Dashboard | Module registry |
| WHOL-REQ-008 | Industry reports listed in reports.md are available to authorized roles. | P1 | Reports | Common reports |
| WHOL-REQ-009 | Optional WhatsApp/PDF invoice flows reuse common integrations. | P1 | WhatsApp/PDF | Common modules |
| WHOL-REQ-010 | Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants). | P0 | Config | BusinessType matrix |

Common billing/inventory requirements are **not** duplicated here — see common-module docs.
