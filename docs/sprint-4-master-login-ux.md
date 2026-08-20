# Sprint 4 — Master Login UX Hardening

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Frontend-only  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Add a private Master Admin entry path without advertising it in the public navbar.

This sprint does **not**:

- change the database
- add a second backend auth system
- put a “Master Admin Login” button in the navbar

---

## What changed

### Master login page

- New public route: `/master/login`
- Page heading: **Prabha Technology / Administration**
- Fields: Email, Password, **Sign In**
- No Register Business / Forgot Password / customer login options
- Uses existing `POST /api/v1/auth/login`
- If a normal Owner/Billing User signs in here, the UI rejects the session with a generic **Invalid email or password** message and does not open the Master console

### Route protection

- Unauthenticated visits to `/master/dashboard` (and other `/master/*` pages except login) now go to `/master/login`
- Expired Master sessions on `/master/*` also return to `/master/login`
- Owner/Billing User still cannot access Master pages (redirected to their own home)
- Backend `master_required` remains the real authorization check

### Footer entry

- Landing footer has a small, low-contrast dot at the bottom-right
- It does **not** say Master Login / Admin Login
- Clicking it opens `/master/login`

---

## Tests

Frontend production build: **green** (1666 modules).

No backend schema or API changes in this sprint. Existing Master auth pytest coverage still applies to `POST /auth/login`.

---

## Changed files

- `frontend/src/pages/master/MasterLoginPage.jsx` — new
- `frontend/src/routes/AppRoutes.jsx`
- `frontend/src/routes/paths.js`
- `frontend/src/routes/ProtectedRoute.jsx`
- `frontend/src/layouts/AuthLayout.jsx`
- `frontend/src/layouts/MasterLayout.jsx`
- `frontend/src/services/apiClient.js`
- `frontend/src/pages/landing/PricingFooter.jsx`

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| No navbar Master Login button | Yes |
| Subtle footer dot opens `/master/login` | Yes |
| Professional Administration login page | Yes |
| Business users cannot use this page to enter Master | Yes |
| Master APIs still require `MASTER_ADMIN` | Yes (unchanged backend) |
| Database unchanged | Yes |

---

**Stopped.** Should I start the next sprint?
