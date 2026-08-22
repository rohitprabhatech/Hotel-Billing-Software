# Sprint Plan — Landing Page Redesign (Premium Billing SaaS)

**Date:** 2026-08-16  
**Status:** Completed  
**Program:** Landing page commercial redesign  
**Product:** Business Billing (Prabha Technology Pvt. Ltd.)  
**Reference:** Uploaded SaaS screenshot — **layout / hierarchy only** (no copy, logo, CRM wording, or brand assets)

---

## 1. Audit — current state

| Area | Current (`frontend/src/pages/HomePage.jsx` ~1000 lines) | Notes |
|------|--------------------------------------------------------|--------|
| Route | `/` via `AppRoutes` → `HomePage` | Auth users redirect to role home |
| Branding | `COMPANY.productName` = **Business Billing**; logo mark **BB** | Keep product name; refine mark |
| Company | `constants/company.js` already has correct Pune address, email, phone, ₹550 | **Do not change** contact facts |
| Theme | MUI `theme/index.js`: teal primary `#1F4E5F`, terracotta secondary, dark mode | Reuse; do **not** copy reference green |
| Navbar | Sticky, centered anchors, Login + Register, hamburger Drawer | Exists; nav labels differ from target |
| Hero | Full-bleed dark gradient, text-first, fade-up | **No** split layout; **no** product/dashboard mockup |
| Badges / trust | Not in reference-like hero badge row + capability strip | Missing |
| Features / modules | Grid copy sections | Content OK-ish; presentation not “premium SaaS” |
| Pricing | `SubscriptionPlanInfo` (informational, no checkout) | Reuse |
| WhatsApp / stock / AI | Partially covered in feature bullets | Need dedicated visual sections |
| Bill preview | Not on landing; `print/BillPreview.jsx` exists in app | Can inspire CSS-only mock |
| Footer | Product / Company / Support columns | Expand (Legal placeholders, Business links) |
| Dark mode | `ThemeModeToggle` + theme palettes | Must redesign intentionally |
| Perf | Monolithic page; no heavy Unsplash hero today | Keep CSS mockups; avoid large image deps |

**Explicitly good to reuse:** `COMPANY` / `SUBSCRIPTION_PLAN`, `PATHS.login` / `PATHS.register`, `ThemeModeToggle`, `SubscriptionPlanInfo`, MUI theme tokens, existing auth redirect, Sora + Source Sans 3 fonts.

---

## 2. Comparison vs reference (layout only)

| Reference pattern | Current landing | Gap |
|-------------------|-----------------|-----|
| Split hero: copy left + product visual right | Full-bleed text hero only | **High** |
| Compact feature badges near hero | Absent | **High** |
| Honest trust / capability strip under hero | Absent / weak | **High** |
| Premium section rhythm (one job per section) | Long “wiki” stacks | **High** |
| Dedicated workflow / bill / stock / WhatsApp visuals | Mostly text | **Medium–High** |
| Sticky commercial nav + clear CTAs | Present, needs label/structure update | **Medium** |
| Multi-column SaaS footer | Partial | **Medium** |

---

## 3. What must change (implementation scope)

### In scope (this sprint)

1. **Restructure** `HomePage` into a premium commercial composition (prefer extracting section components under `frontend/src/pages/landing/` to keep maintainable).
2. **Navbar:** Features · Solutions · How It Works · AI Insights · Pricing · Resources (+ anchors); Login + Register Your Business; keep mobile drawer + dark toggle.
3. **Hero (split):** badge, headline with accent highlight, supporting copy (billing — not CRM), CTAs (Register + Explore Features), soft ₹550 mention, **original CSS/MUI billing dashboard mockup** (sales KPIs, chart, recent bills, top items spanning business types).
4. **Product badges** (compact): Fast Billing, GST, Stock, Reports, Print, WhatsApp Bills, AI Insights, Multi-Business SaaS.
5. **Capability / trust strip** — factual only (e.g. Multi-Business tenant isolation, 24/7 support, ₹550/month plan, One platform: Billing + Stock + Sales + Reports). **No fake “10,000+ businesses” stats.**
6. **Sections:** Core Features (01–08), Billing workflow, Payment methods (Cash / Online), Bill preview mock, Stock + low-stock notifications, Sales analytics mock, AI insights (data-grounded examples), WhatsApp bill flow, Multi-business examples, Security (honest claims only), Owner vs Billing User, Pricing (reuse `SubscriptionPlanInfo` + updated includes), Final CTA, Footer (Product / Business / Company / Legal / Support + company block).
7. **Copy:** “Business” positioning throughout; restaurant/kirana/retail as **examples only**; no hotel-primary framing; no CRM wording.
8. **Responsive:** 320–1440+; single-column hero on mobile; no horizontal scroll; usable CTAs.
9. **Dark mode:** intentional surfaces for hero, mockups, cards, pricing, footer.
10. **Motion:** subtle fade/slide + hover only; respect `prefers-reduced-motion`.
11. **Verify:** Login/Register links; hash nav; dark mode; build; smoke that app routes still work (landing-only FE change — no BE).

### Out of scope

- Copying Aerostic / CRM assets, colors, or text  
- Real Meta/WhatsApp brand assets beyond generic “WhatsApp” wording  
- Invented metrics / certifications  
- In-app SaaS checkout / payment gateway  
- Backend or Owner/Billing app shell redesign  
- New legal page content beyond footer links (Privacy/Terms can be `#` placeholders or simple anchors if pages do not exist yet — document in report)

---

## 4. Proposed file plan

| Action | Path |
|--------|------|
| Modify | `frontend/src/pages/HomePage.jsx` (compose sections) |
| Create | `frontend/src/pages/landing/*` (Hero, Nav, DashboardMock, Features, Workflow, BillPreviewMock, Stock, Analytics, AI, WhatsApp, MultiBusiness, Security, Roles, Pricing wrap, Footer, CapabilityStrip) |
| Touch lightly | `frontend/src/constants/company.js` / `SUBSCRIPTION_PLAN.includes` only if needed for accurate feature list (WhatsApp, stock, notifications) |
| Docs | This plan + sprint completion report after implementation |
| Roadmap | Add **Phase 7 — Landing commercial redesign** row when sprint starts |

**Product name:** keep **Business Billing** (already in product); optional short mark refinement — not “SmartBill” unless you approve a rename.

---

## 5. Acceptance criteria

- First viewport reads as one premium composition: brand + badge + headline + short support + CTA group + dashboard visual (desktop).  
- No CRM positioning; multi-business billing clear.  
- Company contact block matches provided Prabha Technology details exactly.  
- Pricing shows ₹550/month informational (existing pattern).  
- Dark mode + mobile menu verified.  
- `npm run build` OK; Login / Register navigation OK.  
- Stop after report; no auto-next sprint.

---

## 6. Suggested test checklist (post-implementation)

- [ ] Desktop 1280 / 1440 hero split  
- [ ] Mobile 320 / 375 hamburger + stacked hero  
- [ ] Tablet 768  
- [ ] Dark mode all major sections  
- [ ] All navbar anchors scroll correctly  
- [ ] Login → `/login`, Register → `/register`  
- [ ] Footer links / contact mailto & tel  
- [ ] No horizontal overflow  
- [ ] `npm run build`

---

## 7. Risk notes

- Large page: extract components to avoid a 2k-line monolith.  
- Dashboard/bill mocks must be **illustrative UI**, clearly not live tenant data.  
- Legal links: if Privacy/Terms pages are missing, use labeled placeholders and note as residual.

---

**Stopped.** Awaiting approval before any implementation.
