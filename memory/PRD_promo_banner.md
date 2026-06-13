# Feature: Promo Banner + Contact Lead Modal (web SPA)

## Backend — `banner_layer.py` (mounted under `/api`)
Collections: `promo_banners`, `contact_leads`.
- `GET /api/admin/banners` · `POST /api/admin/banners` · `PUT /api/admin/banners/{id}`
  `POST /api/admin/banners/{id}/toggle` · `DELETE /api/admin/banners/{id}`  (admin only)
  → Single active banner: enabling one disables the others.
- `GET /api/public/banner?platform=web|expo` → active banner within date window for that platform.
- `POST /api/public/contact-leads` (public submit) · `GET /api/admin/contact-leads`
  `PATCH /api/admin/contact-leads/{id}` (status: new|handled|archived).

Banner fields: enabled, type(discount|special|announcement|app), placement(top_bar|hero_card|both),
title, subtitle, features[], price, old_price, currency, starts_at, ends_at, show_countdown,
cta_text, cta_mode(url|register|contact), cta_url, accent(hex), badge, show_on_web, show_in_expo.

## Frontend (web SPA)
- `components/PromoBanner.js` — slots `top` (sticky bar) + `hero` (rich card); theme-aware
  (light/dark), live countdown, CTA → url / register / open contact modal. Top bar dismissible.
  Mounted in `LandingPage.js` (dark) and `LandingPageLight.js`.
- `components/ContactModal.js` + `contexts/ContactModalContext.js` — site-wide lead-capture
  modal (`useContactModal().openContact(...)`), bilingual UK/EN, posts to `/public/contact-leads`.
  Provider mounted in `App.js` around the router.
- `pages/AdminMarketingPage.js` — admin config (route `/admin/marketing`, nav in AdminLayout).
  Bilingual UK/EN via local label map keyed on `useLang().lang`. Banner CRUD + live preview +
  Requests (leads) tab. Banner content itself is free-text (any language).

## Bug fixed during this work — `tByEn is not defined` (whole-app crash class)
An i18n sweep had inserted `tByEn(...)` into nested/presentational components without obtaining
it from `useLang()`. Found ALL instances deterministically via a Babel AST scope scan and fixed:
- `LandingPage.js` / `LandingPageLight.js` (6 sections each)
- `MobileNav.js` (MobileBottomNav — was crashing admin pages globally)
- `EstimateResultPage.js` (AuthedCta), `AdminExecutionIntelligence.js` (UniverseCard),
  `AdminV2Portfolio.js` (InquiryRow).
AST scan now reports **0 unbound `tByEn` references**.

## Rebuild web after edits
`cd /app/web && PUBLIC_URL=/api/web-ui GENERATE_SOURCEMAP=false NODE_OPTIONS=--max-old-space-size=3072 yarn build`
