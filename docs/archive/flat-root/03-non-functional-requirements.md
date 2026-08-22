# 03 — Non-Functional Requirements

## NFR-1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Login API response | p95 < 500 ms (local/LAN typical) |
| NFR-1.2 | Item search during billing | p95 < 300 ms for typical catalog sizes |
| NFR-1.3 | Bill finalize transaction | p95 < 800 ms |
| NFR-1.4 | Owner dashboard summary load | p95 < 1.5 s for one day of data |
| NFR-1.5 | Concurrent billing users per tenant | Support ≥ 5 simultaneous billers without bill-number collisions |

## NFR-2 Scalability

| ID | Requirement |
|----|-------------|
| NFR-2.1 | Shared-database, shared-schema multi-tenancy with `tenant_id` isolation |
| NFR-2.2 | Indexes on common tenant-scoped query patterns |
| NFR-2.3 | Stateless API servers (JWT) for horizontal scale of Flask workers |
| NFR-2.4 | Pagination on list endpoints (bills, audit logs, items, reports) |

## NFR-3 Security

| ID | Requirement |
|----|-------------|
| NFR-3.1 | JWT authentication on all protected endpoints |
| NFR-3.2 | Role-based authorization (OWNER vs BILLING_USER) |
| NFR-3.3 | Tenant isolation enforced in every repository query |
| NFR-3.4 | Secrets via environment variables only |
| NFR-3.5 | Password hashing with modern algorithm (e.g., bcrypt/argon2) |
| NFR-3.6 | Secure CORS configuration |
| NFR-3.7 | Rate limiting on auth endpoints |
| NFR-3.8 | No exposure of password hashes, JWT secrets, DB credentials, or internal exceptions |

See also: [17-security.md](./17-security.md)

## NFR-4 Reliability & Data Integrity

| ID | Requirement |
|----|-------------|
| NFR-4.1 | Bill create uses DB transactions (all-or-nothing) |
| NFR-4.2 | Money fields use `DECIMAL` (not float) |
| NFR-4.3 | Unique constraint on `(tenant_id, bill_number)` |
| NFR-4.4 | Soft cancel/void; no hard delete of bills/items/audit by app users |
| NFR-4.5 | Historical snapshots on `bill_items` |

## NFR-5 Usability

| ID | Requirement |
|----|-------------|
| NFR-5.1 | Billing UI optimized for speed (keyboard-friendly search, clear totals) |
| NFR-5.2 | Owner UI optimized for analytics, tables, filters |
| NFR-5.3 | Responsive layouts for desktop billing screens and owner tablets |
| NFR-5.4 | Consistent loading, empty, and error states |
| NFR-5.5 | Confirmation for cancel bill and deactivate item |

## NFR-6 Maintainability

| ID | Requirement |
|----|-------------|
| NFR-6.1 | Backend: MVC + Service + Repository layers |
| NFR-6.2 | Frontend: feature folders by role/domain |
| NFR-6.3 | Clear API versioning under `/api/v1` |
| NFR-6.4 | Flask-Migrate for schema changes |
| NFR-6.5 | Documented sprint plan and acceptance criteria |

## NFR-7 Availability

| ID | Requirement |
|----|-------------|
| NFR-7.1 | Designed for single-region deployment initially |
| NFR-7.2 | Graceful API errors on DB unavailability |
| NFR-7.3 | Health check endpoint for process monitoring |

## NFR-8 Compliance & Auditability

| ID | Requirement |
|----|-------------|
| NFR-8.1 | Immutable application audit trail for sensitive actions |
| NFR-8.2 | Receipt shows GSTIN/FSSAI when configured |
| NFR-8.3 | Exports contain only authenticated tenant data |

## NFR-9 Compatibility

| ID | Requirement |
|----|-------------|
| NFR-9.1 | Modern Chromium/Firefox/Edge browsers |
| NFR-9.2 | Thermal print via browser print CSS (58mm/80mm where practical) |
| NFR-9.3 | MySQL 8.x |

## NFR-10 Observability

| ID | Requirement |
|----|-------------|
| NFR-10.1 | Structured server logs (without secrets) |
| NFR-10.2 | Audit log queryable by owner for business investigation |
| NFR-10.3 | Correlation of request failures via consistent error codes |
