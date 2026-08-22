# Frontend Architecture

**Stack:** React · Vite · MUI · Axios

Layouts: Auth, Owner, Billing, Master. Paths in `routes/paths.js`.

Target: `src/modules/{industry}/` lazy routes gated by feature flags.

Known issue (documented, not fixed here): Owner↔Billing dual-shell navigation.
