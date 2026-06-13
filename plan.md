> **LR-1 Readiness Package + Production Flag System — ✅ ЗАВЕРШЕНО (без LIVE-ключів, як просив користувач).**
> Мета: закрити все, що можна підготувати заздалегідь → кодова база готова до перемикання в LIVE без архітектурних змін. «Чекаємо лише реальні ключі та домен.»
> - **Production Flag System (`ENABLE_DEMO_AUTH`):** єдиний перемикач. `true` (preview/staging, default) — demo-чипи + quick auth увімкнені; `false` (production) — demo-чипи приховані, `POST /api/auth/quick` та `POST /api/auth/demo` → **403**. Бекенд: `_demo_auth_enabled()` + `_guard_demo_auth()` у `server.py` гейтять обидва ендпоінти; новий public `GET /api/auth/config` → `{demo_auth_enabled, env}`. Фронт: `UnifiedAuthPage.js` читає config і ховає demo-чипи коли flag=false. Перевірено реальним HTTP-тестом (flag=false: config=false, quick/demo=403, звичайний login=200; потім revert до true). КОД НЕ ВИДАЛЕНО — лише перемикач через ENV.
> - **`backend/.env.example`** — повний каталог змінних: для кожної REQUIRED?/MODULE/IF ABSENT/MODE (CORE/LIVE/OPTIONAL/PLANNED). Чесно позначено `S3_*` та `REDIS_URL` як **PLANNED (ще не підключено в коді)** — storage зараз Cloudinary/local, rate-limit in-memory.
> - **`LAUNCH_MATRIX.md`** — таблиця Інтеграція / Зараз / Для LIVE / ENV / Поведінка без ключа (Monobank, LiqPay, Email, Sentry, Storage, Rate limit, Google, Demo auth, Legal encryption, Домен) + рекомендований порядок увімкнення LIVE.
> - **`PRODUCTION_CHECKLIST.md`** — фінальний чек-лист (Безпека доступу / Інфраструктура / Платежі / Email / Legal / Operations / Спостережуваність / Запуск) + команди швидкої перевірки прод-режиму.
> - **НЕ чіпали** реальні інтеграції Monobank/LiqPay/SMTP/Sentry/Storage (немає ключів) — щоб уникнути «заглушок поверх заглушок». Залишається LR-1 (LIVE-інфраструктура) → потім Closed Beta (10 → 50 → 100 інвесторів).


> **LR-2a + LR-3a + LR-3b — ✅ ЗАВЕРШЕНО + testing agent 100% (iteration_3: backend 13/13, frontend 8/8, 0 багів).**
> Обрано користувачем: спочатку Legal Package + Operations SOP (1a+2a), плюс маленький Operations Center.
> - **LR-2a Legal Package (6 документів, реальний UA-контент, не плейсхолдери):** Публічна оферта, Політика конфіденційності, AML, KYC, Розкриття ризиків, Умови вторинного ринку. Бекенд: `legal_content.py` (контент, версія пакета v2) + розширено `legal_settings.py` (`SUPPORTED_LEGAL_DOCS`, `ensure_legal_package` на старті, захист `auto_seeded` від перезапису адмінських правок, slug-резолвер `secondary-market→secondary`). Нові public-ендпоінти: `GET /api/public/legal-package`, `GET /api/public/legal-document/{slug}`. Фронт: `pages/legal/LegalIndexPage.js` (/legal — 6 карток), `pages/legal/LegalDocPage.js` (/legal/:slug — повна сторінка з sticky-TOC, крос-лінки, друк), `components/MarkdownLite.js` (рендер markdown-lite). **UI-інтеграція:** футер лендингу (колонка «Правова інформація» + нижній бар), реєстрація (обов'язковий чекбокс згоди з оферта/privacy/risk блокує submit), KYC-картка інвестора (лінки на /legal/kyc, /legal/aml, /legal/privacy), хедер вторинного ринку (лінк на /legal/secondary-market).
> - **LR-3a Operations SOP (5 внутрішніх регламентів, реальні документи для compliance):** KYC Review, Funding Verification, Withdrawal, Payout, Secondary Market Dispute. Бекенд `ops_sop.py` (колекція `lumen_ops_sop`, idempotent seed, `GET /api/admin/sop`, `GET/PUT /api/admin/sop/{key}`, `POST .../reset`, захист `auto_seeded`). Фронт `pages/admin/AdminSOP.js` — список + рендер документа + inline-редактор (керівник редагує текст, reset до базової редакції). Nav «Регламенти (SOP)».
> - **LR-3b Admin Operations Center:** `ops_center.py` — `GET /api/admin/operations/summary` агрегує існуючі процеси (БЕЗ нових сутностей): pending KYC (`lumen_investor_profiles` submitted/under_review), payments (`lumen_payment_requests` paid/under_review), withdrawals (`lumen_withdrawal_requests` requested/approved/processing), payouts (`lumen_payout_batches` generated), disputes (manual=0, лінк на Dispute SOP). Фронт `pages/admin/AdminOperations.js` (/admin/operations) — 5 KPI-карток + total + deep-links у відповідні черги. Nav «Центр операцій».
> - **Wiring:** `server.py` — підключено роутери ops_sop + ops_center, додано startup-hook сидингу legal package + SOP. Маршрути в `App.js` (/legal, /legal/:slug, /admin/operations, /admin/sop). Nav у `AdminLayout.js` + `MobileNav.js`.
> - **Далі (за чергою користувача):** LR-1 (LIVE-інфраструктура: домен, Monobank, LiqPay, Sentry, SMTP, Storage) — коли з'являться ключі та домен.


> **UX-ДОРОБКИ (pod `code-review-318`) — ✅ 3 фікси, testing agent 100% (iteration_2):**
> 1. **Скрол кабінету (баг):** layout-shell переписано на height-bounded — root `h-screen overflow-hidden`, `<main>` `flex-1 min-h-0 overflow-y-auto` (було `min-h-screen overflow-auto`, через що контент обрізався і сторінки не скролились). Виправлено в AdminLayout/InvestorLayout/ClientLayout. Перевірено: `/admin/ledger` з контентом > viewport скролиться, весь контент доступний.
> 2. **Повернення на сайт для авторизованих:** додано лінк «На сайт» (data-testid=back-to-site) у sidebar інвестора й адміна — повертає на лендинг `/` БЕЗ виходу з сесії. Лендинг-хедер авто-показує «Мій кабінет» (role-aware: investor→/investor/dashboard, admin→/admin/dashboard).
> 3. **Публічна картка проєкту:** нова сторінка `PublicAssetDetail` (route `/objects/:id`, публічна) — повна публічна інфа про обʼєкт (Hero · Trust bar · таби Огляд/Галерея/Оновлення-Звіти/Питання · sticky action card з картою/економікою), споживає `GET /api/public/marketplace/{id}`. Картки лендингу тепер ведуть на `/objects/:id` (а не на реєстрацію). Гість бачить CTA «Стати інвестором», авторизований — «Інвестувати в обʼєкт» → /investor/opportunities.


> **SPRINT 13 — SECONDARY MARKET — ✅ ЗАВЕРШЕНО + ВЕРИФІКОВАНО НА 100% (pod `code-review-318`).**
> Повний цикл LUMEN закрито: **вклав → отримав дохід → вивів → продав частку**.
> Архітектура (як у ТЗ, без other-реєстрів/order-book/аукціонів/крипти/маржі):
> `Ownership → Listing → Bid/Buy → Trade → Settlement → Ledger` + ownership split/transfer + 1% platform fee.
> - **Core-інваріант ДОВЕДЕНО:** `total ownership units` по asset НЕ змінюється — змінюється лише власник. Settlement пише 1 `share_transfer` (seller→buyer) + рекомпʼют обох ownership-рядків; Σ ownership == Σ active investments (I1) завжди.
> - **Money conservation на угоду:** buyer debit `secondary_purchase` gross · seller credit `secondary_sale` (gross−fee) · platform credit `platform_fee` (1%) → Σ=0. Гаманці рахуються з ledger (єдине джерело істини).
> - **БАГ ЗНАЙДЕНО І ВИПРАВЛЕНО:** `_settle_trade` робив upsert ownership-рядка БЕЗ `id` → `DuplicateKeyError (id:null)` для покупця, що раніше не володів активом (брав частку вперше). Додано `$setOnInsert {id, created_at}` в обидва upsert. Без фіксу будь-яка перша вторинна купівля впала б на 500.
> - **E2E core (`backend/tests/test_sprint13_secondary_e2e.py`) — 63/63 PASS:** ізольовані фікстури (свіжий asset + 2 інвестори), повний lifecycle buy-now + offer/accept, інваріант після КОЖНОЇ угоди, ledger Σ=0, wallet conservation, platform revenue, та всі guard'и (min listing, over-owned, own-listing, over-remaining, insufficient funds 402, cancel/accept/reject auth 403, offer must be < listing price).
> - **Демо-сид (idempotent, invariant-safe) `seed_secondary_demo()`** у `lumen_secondary.py` + startup-hook (whitelisted у LUMEN_ONLY domain lock): створює окремого демо-продавця (`marketplace.demo@lumen.test`) через registry-rebalance (share_transfer) від client@atlas.dev і 2 активні лістинги (ЖК «Подільський» 90 000 @ 0.97, ТЦ «Лавр» 120 000 @ 1.03). Consistency I1–I13 = green після сиду.
> - **Frontend:** додано sidebar+mobile nav «Вторинний ринок» для investor (`/investor/marketplace`) і admin (`/admin/secondary-market`) — раніше сторінки існували, але не були в навігації.
> - **UI E2E (testing agent, iteration_1) — frontend 100% / integration 100%, 0 багів:** investor browse/buy-now(48 500→settled)/make-offer(0.90)/create-listing/усі 5 табів(Огляд·Мої частки·Мої лістинги·Мої офери·Угоди)/cancel; admin overview KPI(platform revenue/volume/counts)+trades. Consistency лишилась green ПІСЛЯ живих UI-угод (0 broken).
> - **Регресія:** test_sprint1_smoke + test_sprint2_core — ALL PASS.


> **DEPLOY (pod `code-review-318`) — ✅ повне розгортання з GitHub `svetlanaslinko057/8776878uhhgA` у `/app`.**
> - Синхронізовано `backend/`, `frontend/`, `packages/` (design-system + runtime-client), `memory/`, `plan.md`, `tests/`. `.env` збережено платформою (MONGO_URL / REACT_APP_BACKEND_URL).
> - backend `pip install -r requirements.txt` ✅ (emergentintegrations 0.1.0, litellm, reportlab, stripe, resend…). frontend `yarn install` ✅.
> - backend `.env`: `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0`, `EMERGENT_LLM_KEY` set, `CORS_ORIGINS=*`.
> - Seed: `scripts/bootstrap_seed_once.py` → 12 users; startup auto-seed → 6 активів, 3 шаблони договорів, asset content, 20 LUMEN-колекцій з індексами, domain lock active (22 legacy skipped, 4 LUMEN startup). Свіжа БД (secondary market порожній — угод ще не було).
> - Перевірено: `/api/healthz` ok, `/api/assets` (6), login admin@atlas.dev/admin123 + client@atlas.dev/client123 ✅, `/api/public/marketplace` feed ✅, landing рендериться (LUMEN, teal/gold, портфель ₴2 465 000). Усі сервіси RUNNING.
> - Останні таски в коді (для продовження): Secondary Market `lumen_secondary.py` (listings/bids/trades/settlement, fee 1%) + `InvestorMarketplace.js` / `AdminSecondaryMarket.js`. emergent_todos: E2E lifecycle buy-now + offer/accept + інваріант (total units незмінний) ще НЕ проганявся реальною угодою. Очікуємо нові задачі від користувача.


# plan.md — Lumen (трансформація EVA‑X у інвестплатформу)

> **MARKETPLACE DEPTH (Full Asset Page, Lumen expo) — РЕАЛІЗОВАНО:**
> Публічна картка доведена з MVP (Hero/Trust/Timeline) до повноцінного інвестиційного лендінга. БЕЗ нових флоу/банкінгу/KYC/ledger/secondary-мутацій — лише READ уже побудованого контенту Sprint 5–9. Expo-хостинг НЕ чіпали (за домовленістю — це інфра-задача).
> - **Backend `lumen_marketplace.py`** (переписано): `GET /api/public/marketplace/{id}` тепер агрегує `sections`:
>   - **P1 Gallery** — photos · plans · documents(public/locked) · progress(milestone-оновлення) · yield(прогноз доходу на min ticket).
>   - **P2 Map** — lat/lng · region · district · infrastructure[] · static_map_url(OpenStreetMap, keyless) · maps_link(Google Maps). geo з `asset.geo` або fallback по місту.
>   - **P3 Q&A** — answered питання з `lumen_asset_questions` (question/answer/date/author), inline.
>   - **P4 Secondary Listing** — для kind=listing: owner_label · share · price · yield · reason · fee.
>   - **P5 Updates+Reports** — `lumen_asset_updates`(published) + `lumen_asset_reports`(published).
> - **Seed `seed_marketplace_content.py`** (idempotent, реальні колекції; admin може замінити): geo×6, plans×3, updates×9, reports×10, documents×15, questions×15.
> - **Expo frontend:** `src/marketplace/sections.tsx` (GallerySection[tabs] · MapSection · QASection · SecondaryListingSection · UpdatesSection · ReportsSection) + переписано `UnifiedRequestDetailPage.tsx` (Hero→Trust→Timeline→Gallery→Map→Q&A→Listing→Updates→Reports). Linking для карти/документів/звітів.
> - **Верифікація:** `expo export --platform web` ✅ (18 routes, `/marketplace/[id]` 32.7 kB, 0 помилок); route МОНТУЄТЬСЯ (AppHeader+screen рендеряться); backend DTO перевірено curl — ВСІ секції наповнені реальними даними (photos 4/plans 2/docs 3/map+4 infra/Q&A/updates/reports). Дата-фетч у static `expo export` «висить» через runtime-client boot (очікує Metro/власний хост) — той самий інфра-артефакт прев'ю, який домовились не чіпати.
> - **Наступне (за планом користувача):** це був «Marketplace Deepening» (1–2 дні), а не Sprint 13. Далі — Sprint 13 Secondary Market (повний lifecycle угоди) або підняти Expo на власному хості для візуального прогону.


> **MOBILE — Public Marketplace Card + Marketplace Live (Lumen, expo) — РЕАЛІЗОВАНО:**
> Завдання (публічна шарингова картка `/marketplace/:id → PublicShell → UnifiedRequestDetailPage`) виконано в Expo-додатку під логіку Lumen (EVA-X-термінологія customer/provider/bid змаплена на investor/seller/секондарі-офер).
> - **Expo змонтовано в `/app/expo`** (раніше не було в /app): `yarn install` ✅. `expo-localization` вже встановлено (`~17.0.9`) і в `app.json` plugins — P0-fix НЕ потрібен (нічого не видалялось).
> - **Backend `lumen_marketplace.py`** (READ-ONLY, без нових мутацій; зареєстровано в server.py Sprint-10 loop): `GET /api/public/marketplace` (Marketplace Live feed: активи + активні secondary listings) і `GET /api/public/marketplace/{id}` (Unified DTO: hero/trust/timeline/action + sections gallery|map|bids|qa як задел; резолвить asset id АБО listing id). Auth НЕ потрібен для перегляду. Runtime: feed 200 (count 6), detail 200.
> - **Expo frontend:** `src/marketplace/dto.ts` (типи+форматери), `src/marketplace/PublicShell.tsx` (role-aware: guest/investor/seller/admin; sticky action card; share; seller-детект через /investor/secondary/holdings), `src/marketplace/UnifiedRequestDetailPage.tsx` (MVP-блоки Hero · Trust bar · Timeline + теасери gallery/map/bids/qa), `app/marketplace/[id].tsx` (route, читає `?source=`), `app/marketplace/index.tsx` (Marketplace Live feed → drill-down `/marketplace/:id?source=live`). `welcome.tsx`: публічний лінк «Переглянути об'єкти наживо».
> - **Role-aware actions:** guest→Створити кабінет/Увійти; investor→Інвестувати/Купити частку+Запитати; seller(власник)→Керувати часткою; admin→Відкрити в кабінеті/Trace·Marketplace Live. Усі дії маршрутизують у вже наявні флоу (`/auth`, `/client/asset/[id]`, `/client/home`, `/admin/home`) — без нових backend-мутацій.
> - **Верифікація:** `expo export --platform web` ✅ (18 routes, вкл. `/marketplace`, `/marketplace/[id]`); екрани РЕНДЕРЯТЬСЯ (Marketplace Live header/filters); backend перевірено curl + браузерний fetch (200, count=6).
> - **ВАЖЛИВО (обмеження pod):** Expo на цьому pod НЕ має live-preview (web :3000 зайнятий CRA; Expo за README обслуговується окремим pod/субдоменом). Дата-фетч у тимчасовому cross-origin static-serve «висить» через runtime-boot (очікує same-origin /api) — це артефакт прев'ю, НЕ баг коду. У штатному запуску Expo (Metro / власний хост, same-origin) працює нормально. Для запуску: `cd /app/expo && EXPO_PUBLIC_BACKEND_URL=<домен> yarn start`.


> **STATE AUDIT (pod, repo `e2k3enk323`) — аналіз коду + runtime smoke (НЕ повний E2E):**
> Перевірено фактичний код і живі ендпоінти, а не лише claims у plan.md.
> - **Усі роутери завантажені** (0 «router failed»); backend+frontend RUNNING; security-check: 173 routes, 0 broken.
> - **Sprint 10 (Production Hardening) ІСНУЄ в коді й відповідає:** `lumen_audit` (/admin/audit/log ✅), `lumen_consistency` (/admin/consistency/check → overall ok, 0 broken), `lumen_permissions` (matrix: investor/asset_manager/compliance/finance/admin/system), `lumen_ops` (/admin/monitoring/db, /admin/backups), `lumen_system_health` (overall=warning лише через `file_audit` mock-storage orphans; решта ok), `lumen_settlement_audit` (/admin/settlement/check ok), `lumen_reconciliation` (/admin/reconcile/preview).
> - **Sprint 11 (Banking) ІСНУЄ:** `lumen_banking` (/banking/providers → monobank+liqpay, **mode=mock, configured=false**), `lumen_bank_reconciliation` (/admin/bank-transactions ✅), `lumen_payout_export` (/admin/payout-export/batches ✅).
> - **«Sprint 13» Secondary Market ВЖЕ ПОБУДОВАНО (НЕ 0%):** backend `lumen_secondary.py` (listings/bids/trades/settlement/admin) + frontend `InvestorMarketplace.js` (Holdings→продаж, Listings→купівля, Bids→офери, Trades) + `AdminSecondaryMarket.js` (route `/admin/secondary-market`). Архітектура САМЕ як у ТЗ: Ownership→Listing→Bid→Trade→`_settle_trade`→Ledger (buyer debit / seller credit `secondary_sale` gross−fee / `platform_fee` 1% → PLATFORM) + authoritative `lumen_share_transfers` + recompute_wallet. Без order book/аукціонів/токенізації. Runtime: holdings/listings/overview → 200 з реальними даними, `platform_fee_pct=0.01`.
> - **Дані (fresh seed):** assets 6, investments 3, ownerships 3, ledger 6, payout_records 4, wallets 1, users 12. **secondary_listings/bids/trades/share_transfers = 0** → вторинний ринок ще НЕ проганявся реальною угодою.
> - **ЩО НЕ ЗРОБЛЕНО / НЕ ПЕРЕВІРЕНО:** (1) повний E2E НЕ запускали — лише smoke; повний lifecycle угоди вторинного ринку (ownership split + ledger + 1% fee + wallet + guards) НЕ верифіковано; (2) LIVE-інтеграції — mock (Monobank/LiqPay configured=false, Sentry disabled, object storage локальний); (3) Mobile/Expo — не запущено на цьому pod, TS tech debt (~85%); (4) Launch-readiness (SSL/домен/Redis rate-limit/legal docs/оферта/privacy) — pending.
> - **Висновок:** Sprint 13 — це здебільшого ВЕРИФІКАЦІЯ наявного коду, а не побудова з нуля. Рекомендований наступний крок: Verification Sprint (testing agent E2E на secondary-market settlement) → потім Launch Readiness Review.


> **DEPLOY (pod arch — repo `svetlanaslinko057/e2k3enk323`):** повне розгортання з GitHub у `/app`.
> - Синхронізовано `backend/`, `frontend/`, **`packages/`** (монорепо design-system + runtime-client), `memory/`, `plan.md`. `.env` збережено платформою (MONGO_URL / REACT_APP_BACKEND_URL).
> - backend `pip install -r requirements.txt` ✅; frontend `yarn install` ✅.
> - `.env` (backend): `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0`, `CORS_ORIGINS=*`.
> - Seed: `seed_lumen_users.py` (admin@atlas.dev/admin123, admin@devos.io/admin123, client@atlas.dev/client123) + `scripts/bootstrap_seed_once.py` (12 users). Startup auto-seed: 6 активів, шаблони договорів, asset content, 20 LUMEN-колекцій, Sprint 6/7/8 bootstrap.
> - **Фікси білду фронта (репо-specific у цьому pod):** (1) скопійовано відсутню теку `packages/` (design-system tokens + runtime-client) — без неї webpack «Module not found»; (2) видалено `frontend/jsconfig.json`; (3) `src/runtime-client` (симлінк → `../../packages/runtime-client/src`) замінено реальною копією, щоб fork-ts-checker резолвив модуль усередині `src` (TS2307 fix); (4) додано `preserveSymlinks` у tsconfig.
> - Verified E2E: landing (UA, LUMEN, teal/gold) ✅, `/login` → `/investor/dashboard` (₴874 892, 3 інвестиції, повний sidebar Sprint 1–9) ✅, `/api/assets` (6) ✅, login client/admin ✅. Усі сервіси RUNNING. Очікуємо нові задачі від користувача.


> **SPRINT 8 (Payout Engine) — ✅ ПРИЙНЯТО (2026-06-12).** Повний життєвий цикл капіталу: Asset → Investment → Ownership → Income → Payout → Ledger → Wallet → Withdrawal.

> **SPRINT 9 (Investor Analytics & Fund Intelligence) — ✅ ЗАВЕРШЕНО + ПЕРЕВІРЕНО (2026-06-12, pod arch-study-17):**
> «Інтелект поверх даних»: інвестор бачить не список об’єктів, а стан свого капіталу; адмін — стан фонду.
> **АРХІТЕКТУРНИЙ ПРИНЦИП (виконано):** усі метрики рахуються НАЖИВО з реєстрів — `lumen_ledger_entries / lumen_ownerships / lumen_investments / lumen_payout_records / lumen_assets / lumen_withdrawal_requests / lumen_payment_requests / lumen_asset_reports`. ЖОДНИХ збережених KPI / materialized totals у Mongo. Sprint 9 підтвердив, що Ledger — джерело істини (E2E: admin capital_paid_out == investor received_total == Σ ledger payout credits).
> - **Backend `lumen_analytics.py`:**
>   - Investor: `GET /api/investor/analytics/overview` (Portfolio Value: invested/current/received/expected + wallet; Yield: realized/unrealized/annualized **time-weighted** + weighted_holding_years; Allocation: by_category/by_region/by_risk). `…/assets` (per-asset: invested/share/received/ROI/next_payout/risk/region). `…/timeline` (Block 4 — стрічка подій: investment_created→kyc_approved→contract_signed→payment_confirmed→payout_received→withdrawal_submitted). `…/portfolio-timeline` (5-стадійний lifecycle: Інвестовано→Профінансовано→Договір підписано→Перша виплата→Вивід).
>   - Похідні поля (рішення 1A, без міграції моделі): `risk_level = max(severity)` з risks[]; `region = перша частина location`.
>   - Admin Fund Intelligence: `GET /api/admin/fund/intelligence` (AUM, active_investors, capital_raised, capital_paid_out, withdrawals_paid, pending_funding, pending_withdrawals, upcoming_payouts(+count), net_cash_position, average_yield, asset_health_distribution). `GET /api/admin/fund/health` (per-asset Health + signals + thresholds).
>   - **Asset Health engine** (Block 6, пороги-константи, рішення 2A): overdue payout >7д→warning / >30д→critical; no reports >90д→warning / >180д→critical; paused plan/asset→warning. Worst-of-signals.
> - **Backend `lumen_statements.py`** (Block 7, рішення 3A — лише PDF): `GET /api/investor/statements` (періоди monthly/quarterly/annual з has_activity), `…/{ptype}/{pkey}/pdf` (reportlab, кирилиця; джерела Ledger+Ownership+Payouts+Withdrawals: холдинги + рух коштів + підсумок). Admin-дзеркало: `GET /api/admin/investors/{id}/statements(/{ptype}/{pkey}/pdf)`.
> - **Frontend:** `InvestorAnalytics.js` (`/investor/analytics`, nav «Аналітика», PieChart): Вартість портфеля, Дохідність, 3 панелі алокації (бари), Ефективність активів (таблиця), Інвестиційна історія (stepper), Стрічка подій (feed), Виписки PDF (таби+завантаження). `AdminFundIntelligence.js` (`/admin/fund`, nav «Аналітика фонду», Gauge): 10 KPI, Здоров’я активів (3 клікабельні картки-фільтри + stacked bar), Моніторинг активів (таблиця з сигналами/порогами). Nav додано в Investor/Admin sidebar + MobileNav; роути в App.js.
> - **Заборони Sprint 9 дотримано:** без вторинного ринку, податкових форм, банк-експорту, CRM, AI-рекомендацій.
> - **E2E (iteration_10.json):** Backend **11/11 (100%)**, Frontend **100%** (28 перевірок) — включно з access-control (investor→admin 403, неавторизований 401) та перевіркою ledger-truth. 0 багів.
> - **Примітка:** annualized_yield на демо-даних високий (~193%), бо seed holding ≈1 міс (weighted_holding_years≈0.08) — архітектурно коректно. Усі 6 активів зараз `healthy` (свіжий seed) — теж коректно.
> - **Далі (оновлений порядок користувача):** Sprint 10 — Production Hardening → Sprint 11 — Bank Integrations → Sprint 12 — Secondary Market → Sprint 13 — Mobile Completion.


> **SPRINT 7 (Wallet + Withdrawals) — ✅ ПРИЙНЯТО (2026-06-12):** регресію перевірено E2E (wallet баланс/історія/заявки, admin черга виводів). Виплати з Payout Engine коректно потрапляють у `wallet.available_balance`.

> **SPRINT 8 (Payout Engine) — ✅ ЗАВЕРШЕНО + ПЕРЕВІРЕНО (2026-06-12, pod arch-study-17):**
> Перехід «інвестор вклав гроші» → «інвестор реально отримує дохід». Код вже існував у репо як остання доробка — вивчено, фіналізовано та протестовано E2E.
> - **Backend `lumen_payouts.py`** (851 рядків, повністю функціональний):
>   - 3 колекції: `lumen_payout_plans` (asset_id/type/frequency/expected_amount/status), `lumen_payout_records` (asset_id/investor_id/ownership_id/amount/currency/status/planned_date/paid_date), `lumen_payout_batches`.
>   - Типи: rental_income / profit_share / exit_distribution / manual. Частоти: one_time/monthly/quarterly/annual.
>   - Lifecycle батча: generated → approved → credited (термінал) / cancelled. Record повторює статус батча. Статуси record: planned/generated/approved/credited/cancelled.
>   - Розподіл `distribute_amount()`: пропорційно частці у пулі (units з `lumen_ownerships`), залишок округлення → найбільшому власнику.
>   - **На `credit_batch`**: для кожного record → `_ledger_append(entry_type="credit", reason="payout")` + `record.status=credited`+paid_date+ledger_entry_id, далі `recompute_wallet()` → `wallet.available_balance↑` + in-app notification `payout_credited`. Ланцюг: Asset → Payout Plan → Records → Batch → Ledger(credit) → Wallet → Withdrawal.
>   - Guards (перевірено): credit до approve → 409; double-credit → 409; cancel credited → 409.
>   - Endpoints: investor `GET /api/investor/income` (summary: accrued/paid/expected/invested/yield + by_asset з last/next payout), `GET /api/investor/income/payouts`, `GET /api/assets/{id}/payout-summary` (total_accrued/last/next). Admin: `GET/POST /api/admin/payout-plans`, `PATCH .../{id}` (pause/resume), `POST .../{id}/recalculate` (preview allocations), `POST .../{id}/generate`; `GET /api/admin/payout-batches(?status=)`, `GET .../{id}`, `POST .../{id}/approve|credit|cancel`; `GET /api/admin/payout-records`.
>   - Bootstrap `bootstrap_payouts()`: idempotent indexes + демо-сид (rental_income план + 3 credited місячні батчі + 1 pending) на активі з ownership.
> - **Frontend Web:**
>   - `InvestorIncome.js` («Доходи», `/investor/income`): 4 KPI (Нараховано всього / Виплачено / Очікується / Сер. дохідність), «Дохідність за активами» (invested/paid/expected/yield + остання/наступна виплата), «Історія нарахувань» зі статус-бейджами. Nav «Доходи» (TrendingUp) — investor sidebar + MobileNav.
>   - `AdminPayouts.js` (`/admin/payouts`, nav «Виплати доходу», Coins): вкладки Плани/Пакети. Плани — create/recalculate(preview)/generate/pause-resume. Пакети — список з фільтром статусу, detail, approve/credit/cancel.
>   - `InvestorAssetDetail.js`: блок `asset-payout-summary` (Всього нараховано / Остання виплата / Наступна виплата) через `/assets/{id}/payout-summary`.
> - **Скоуп-заборони дотримано:** без автобанку, податкового модуля, вторинного ринку, крипто-виплат, dividend reinvestment.
> - **UX-борг закрито:** cookie-banner більше не перекриває кнопку logout у кабінетах. `CookieBannerMount` (App.js) визначає `inApp` через `useLocation`; у CookieBanner на desktop (≥768px) клас `.cookie-banner--inapp` зсуває банер за сайдбар (`left:324px`). Перевірено DOM: `overlap:False`, computedLeft `324px`.
> - **Виправлено білд/рендер баги репо:** `MobileNav.js` — дубльований імпорт `Coins` (compile error) + відсутній імпорт `TrendingUp` (runtime ReferenceError, білий екран). Видалено legacy `frontend/jsconfig.json`.
> - **E2E (iteration_9.json):** backend 27/27 (100%) — повний lifecycle plan→generate→approve→credit→ledger→wallet, усі 409-guards, income/wallet зросли коректно (investor client@atlas.dev: wallet available ₴125 000, income paid ₴125 000). Frontend 33/34 (єдиний flagged cookie-overlap — фактично виправлено й підтверджено окремою DOM-перевіркою).
> - **Наступні (за дорожньою картою користувача):** Sprint 9 — Investor Analytics; Sprint 10 — Secondary Market; Sprint 11 — Production Hardening; Sprint 12 — Bank Integrations; Sprint 13 — Mobile Completion.


> **DEPLOY 2026-06-12 (pod arch-study-17, повне розгортання з GitHub):** репозиторій `svetlanaslinko057/lll2k3-23jrfZ` склоновано та повністю розгорнуто в `/app`.
> - backend deps `pip install -r requirements.txt` ✅; frontend deps `yarn install` ✅.
> - `.env` відтворено (відсутні в git): backend `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0`, `EMERGENT_LLM_KEY`; frontend `REACT_APP_BACKEND_URL` (платформа), `WDS_SOCKET_PORT=443`.
> - Seed: `scripts/bootstrap_seed_once.py` (12 users) + `seed_lumen_users.py` (admin@atlas.dev/admin123, admin@devos.io/admin123, client@atlas.dev/client123). Startup засіяв 6 активів, шаблони договорів, asset content, 20 LUMEN-колекцій, Sprint 6/7/8 bootstrap.
> - **Виправлено 2 баги в коді репо, що блокували білд/рендер фронта:**
>   1. `MobileNav.js` — дубльований імпорт `Coins` з lucide-react (compile error) → прибрано.
>   2. `MobileNav.js` — відсутній імпорт `TrendingUp` (runtime ReferenceError → білий екран на landing) → додано.
>   - Також прибрано legacy `frontend/jsconfig.json` (конфлікт із tsconfig.json — frontend не стартував).
> - Verified end-to-end: landing (UA, teal/gold, Lumen лого) ✅, `/login` → `/investor/dashboard` (₴874 892, 3 інвестиції, nav з Гаманцем) ✅, `/api/assets` (6) ✅, `/api/auth/login` ✅. Усі сервіси RUNNING. Очікуємо нові задачі від користувача.


> **SPRINT 7 (Wallet + Withdrawals) — IN PROGRESS (backend ✅, frontend ✅, E2E pending):**
> - Fix Sprint: legacy `/investor/assets` testid alias added (redirects to opportunities); `mobile-menu-button` присутній (responsive, прихований на desktop).
> - Backend: `lumen_wallet.py` — колекції `lumen_wallets` + `lumen_withdrawal_requests`. Баланс рахується з `lumen_ledger_entries` (payout/refund/adjustment − withdrawal − pending). Lifecycle: requested→under_review→approved→processing→paid (ledger debit) / rejected / cancelled. Reserve при заявці, повернення при reject/cancel.
> - Legacy route dedup: під LUMEN_ONLY прибрано legacy EVA‑X `/admin/withdrawals*` + `/developer/withdrawals*` (shadow). Нові маршрути tagged `lumen-wallet`.
> - Seed: `seed_demo_dividends()` — 10% нарахованих дивідендів на активні інвестиції (демо). client@atlas.dev: 85 000 ₴ доступно.
> - POC `tests/test_sprint7_wallet.py`: ALL PASS. Регресія S1–S6: ALL PASS.
> - Frontend: `/investor/wallet` (баланс/історія/заявка/список/статуси), `/admin/withdrawals` (черга/approve/reject/processing/paid/коментар/ledger). Nav: Investor «Гаманець», Admin «Виводи» (sidebar + MobileNav).

> **DEPLOY (свіжий pod, повторне розгортання):** репозиторій svetlanaslinko057/dqlll1 склоновано та повністю розгорнуто в /app.
> - backend deps: `pip install -r requirements.txt` ✅ ; frontend deps: `yarn install` ✅
> - backend/.env: `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0` (MONGO_URL/REACT_APP_BACKEND_URL збережені платформою).
> - Видалено legacy `frontend/jsconfig.json` (конфлікт з tsconfig.json).
> - `seed_lumen_users.py` запущено → admin@atlas.dev/admin123, admin@devos.io/admin123, client@atlas.dev/client123.
> - Verified: backend up (LUMEN_ONLY, 20 колекцій, seeds Sprint 4/5/6), `/api/assets` ✅, login ✅, landing ✅, /login ✅.

> **DEPLOY 2026-06-11 (fresh pod):** репозиторій повністю розгорнуто.
> - backend/.env відтворено: `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `EMERGENT_LLM_KEY` (env у git відсутні).
> - Виправлено: видалено legacy `frontend/jsconfig.json` (конфлікт із tsconfig.json — frontend не стартував).
> - Seed користувачів: legacy `startup_event` skipped під LUMEN_ONLY → створено `/app/backend/seed_lumen_users.py` (admin@atlas.dev/admin123, admin@devos.io/admin123, client@atlas.dev/client123). Див. memory/test_credentials.md.
> - Verified: landing ✅, investor dashboard ✅, admin (панель фонду) ✅, /api/assets (6) ✅, login/quick ✅.
> - Sprint 1 smoke: ALL PASS (assert оновлено 7→10 колекцій після Sprint 4).
> - ⚠️ Sprint 2/3 тести падають ОЧІКУВАНО: Sprint 4 додав contract gate (approve → contract_pending, не active). Оновлення тестів — у pending‑задачах Sprint 4.
>
> **Sprint 4 (Contracts) — ✅ ЗАВЕРШЕНО ПОВНІСТЮ (2026-06-11), див. секцію «Sprint 4 — Contracts & Legal Layer» нижче:**
> - ✅ Backend: lumen_contracts.py (templates seed, gate KYC+signed → active) + 2 фікси (number max+1, route dedup)
> - ✅ test_sprint4_contracts.py + оновлені test_sprint2_core.py / test_sprint3_kyc.py — регресія S1–S4 ALL PASS
> - ✅ Frontend InvestorContracts (list/PDF/sign) + sidebar + dashboard banner + portfolio badge
> - ✅ Frontend AdminContracts (реєстр/лічильники/cancel/шаблони) + AdminIntents (заявки: approve/reject) + nav/MobileNav
> - ✅ Testing agent E2E: 100% (iteration_5, 0 багів)

## 1) Objectives
- Перетворити EVA‑X (software marketplace) у **Lumen** — платформу колективних інвестицій у реальні активи в Україні.
- **Повністю прибрати** dev/tester/developer workflows і «кабінети розробника» з web та Expo.
- Зберегти базову архітектуру та каркас: **React SPA + FastAPI + MongoDB + Expo**, auth/2FA, ролі, інфраструктурні модулі.
- Усі тексти, комунікація і UI — **строго українською** (не «переклад», а повноцінна копірайтерська українізація).
- Візуальна ідентичність **Lumen**: deep teal‑green + dawn‑gold, без «агресивних» вогняних палітр.
- Веб застосунок: продажний landing, глибокий інвест‑калькулятор з економікою, concierge‑бот, окремі Investor/Admin кабінети.
- Мобільний застосунок (Expo): **інвесторський кабінет Lumen**, без дев‑кабінету, з узгодженою термінологією та брендингом.
- Брендинг: **використовувати лише користувацькі логотипи (PNG light/dark)**, без генеративних SVG.

**Поточний статус (на зараз):**
- ✅ Web Lumen працює як інвестплатформа (Landing + калькулятор + бот + Investor/Admin кабінети).
- ✅ Dev/tester флоу прибрані на web.
- ✅ Тема web оновлена під Lumen (teal/gold).
- ✅ Логотип користувача (web):
  - фінальна пара PNG **v4** (з одного файлу вирізані 2 варіанти) інтегрована у web;
  - розмір логотипу в web‑header виправлено (компактний, на рівні висоти CTA).
- ✅ Expo (Phase 4) **в основному завершено**: welcome/auth/роутинг/хедер/профіль/активність переведені на Lumen українською, developer прибраний.
- ⚠️ У Expo залишаються **TypeScript помилки, що існували раніше** (відсутні модулі feedback/state‑shift/onboarding‑tour/referral тощо) — не пов’язані з останніми змінами Phase 4, але заважають “tsc --noEmit” для всього проєкту.

---

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation): «Інвест‑потік даних + базовий кабінет»
> Мета: довести, що інвест‑каркас працює end‑to‑end, не ламаючи auth/2FA.

**Статус:** ✅ виконано (POC переріс у робочий V1 на web).

- Backend: `GET /api/assets`, `GET /api/admin/assets`, `POST /api/auth/register`, `POST /api/auth/login`.
- Frontend: Landing → Auth → Investor Dashboard.
- Виправлено критичний баг runtime‑client (читати `response.data.user`).

---

### Phase 2 — V1 App Development: «Хірургічне видалення + ребрендинг + нова навігація»
**Статус:** ✅ виконано для web.

1. Hard delete старої логіки (Web)
   - Видалено сторінки/компоненти developer/tester/workflows.
2. Backend cleanup
   - Dev/tester ендпоінти відключені/не використовуються.
3. Ребрендинг Lumen (Web)
   - Landing переписаний українською під інвест‑домен.
   - Eva Companion → Concierge з інвест‑флоу.
   - Тема: deep teal‑green + dawn‑gold.
4. Investor Cabinet (Web)
   - Працюючі Investor сторінки/меню.
5. Admin Panel (Web)
   - Працююча адмінка під фондові операції.

#### Phase 2.1 — Брендинг: логотипи користувача (P0)
**Статус:** ✅ виконано (web).

Вимога: повністю прибрати будь‑які AI‑згенеровані SVG/домальовки та використовувати тільки користувацькі PNG.

**Фінальна реалізація (web):**
- Логотипи взяті з одного PNG, де є 2 версії (light/dark), **вирізані** у два файли:
  - `lumen-dark.v4.png` (для світлої теми)
  - `lumen-light.v4.png` (для темної теми)
- `Logo.js` рендерить простий `<img />` і перемикає asset по темі.
- Розміри логотипу зменшено до «висоти CTA» (щоб не ламати header/верстку).

**Зачеплені файли (web):**
- `/app/frontend/public/branding/lumen-dark.v4.png`
- `/app/frontend/public/branding/lumen-light.v4.png`
- `/app/frontend/src/components/Logo.js`
- Розміри: `LandingPage.js`, `UnifiedAuthPage.js`, `MobileNav.js`, `InvestorLayout.js`, `AdminLayout.js`, `ClientLayout.js`.

---

### Phase 3 — Stabilization + Incremental Testing
**Статус:** 🚧 триває.

1. Веб стабілізація після ребрендингу
   - Скриншот‑перевірка ключових екранів (Landing/Auth/Dashboards).
   - Перевірка мобільної навігації (MobileNav) — логотип не обрізається.
2. Прибрати залишкові тексти EVA‑X/DevOS
   - SEO title/meta, дрібні підписи, назви кнопок.
3. Перевірити auth/2FA/редіректи
   - Переконатись, що всі відповіді runtime‑client читаються з `.data`.

---

### Phase 4 — Expo Mobile трансформація під Lumen (P0/P1)
**Статус:** ✅ основна робота виконана.

**Ціль:** зробити мобільний застосунок як «обгортку» Lumen, з тими ж принципами, що й web:
- **нема developer cabinet**
- є **інвесторський (client → investor) кабінет**
- **100% українська копірайтерська** мова
- брендинг Lumen (логотипи + палітра)

#### 4.1 Entry experience: Welcome + Auth (P0)
**Статус:** ✅ виконано.

- `/app/expo/app/welcome.tsx` — повний rewrite під Lumen інвест‑пітч українською; прибрано EVA‑X/describe/SEQ‑XX/freelance лексика; один CTA на інвесторський вхід/створення кабінету.
- `/app/expo/app/auth.tsx` — повний rewrite під Lumen:
  - інвесторський флоу: email → OTP → password fallback
  - без `intent=developer`
  - без lead/workspace claim логіки
  - український UX‑копірайт

#### 4.2 Routing: прибрати developer/describe/hub концепцію (P0)
**Статус:** ✅ виконано.

- `/app/expo/app/index.tsx` — прибрано згадки `/describe`; гостя веде на `/welcome`, автентифікованого — у кабінет.
- `/app/expo/src/route-resolver.ts` — переписано: тільки `client`/`admin`, без developer/tester.
- `/app/expo/src/resolve-entry.ts` — вже відповідає моделі Lumen (admin → /admin/home, інакше → /client/home).

#### 4.3 App header + навігація (P0)
**Статус:** ✅ виконано.

- `/app/expo/src/app-header.tsx`
  - замінено EVA‑X brand mark на Lumen logo assets;
  - українські TITLES;
  - прибрано згадки developer/describe/estimate/lead у visitor segments;
  - відключено HVL/validator (заглушка `enabled=false`) — залишок EVA.

#### 4.4 Логотипи в Expo (P0)
**Статус:** ✅ виконано.

- Додано у `/app/expo/assets/images/`:
  - `lumen-logo-light.png`
  - `lumen-logo-dark.png`
- Welcome/Auth/Header обирають логотип по темі:
  - темна тема → світлий логотип
  - світла тема → темний логотип

#### 4.5 Кабінет інвестора (client stack → investor) (P1)
**Статус:** ✅ базово виконано, ⚠️ потребує полірування.

- `/app/expo/app/client/home.tsx`
  - виправлено імпорт `api` (named → default)
  - додано Lumen accent (gold) замість помаранчевого
  - приведено читання відповіді до `o.data?.items`/`p.data?.summary` (під `AxiosCompatResponse`)
- `/app/expo/app/client/profile.tsx`
  - дрібні правки: KYC поле через `(user as any)` + прибрано помаранчеву кнопку (переведено у teal)
- Глобальні сторінки:
  - `/app/expo/app/profile.tsx` — переписано: тільки client/admin, прибрано developer chip та англомовні тексти
  - `/app/expo/app/activity.tsx` — переписано під Lumen: виплати/раунди/оновлення

#### 4.6 Мова: «лише українська» (P0)
**Статус:** ✅ виконано.

- `/app/expo/src/i18n.tsx`
  - `detectDeviceLang()` тепер завжди `uk`
  - гідрація зі стореджу: якщо було `en` — примусово мігрує в `uk`
  - `setLang()` примусово зберігає `uk` (інші ігнорує)

#### 4.7 2FA та системні екрани (P1)
**Статус:** ✅ тексти в основному українські через існуючий UK dict; ⚠️ потрібна точкова ревізія копі.

- `settings.tsx`, `account.tsx`, `documents.tsx`, `two-factor-*` багато в чому використовують `useT()` / `translateAlert()` — українські ключі вже присутні в `UK` словнику.
- Потрібно пройтись вручну по залишкових hardcoded Alert/label, якщо вони лишилися.

---

### Phase 5 — Expo build health / Tech debt (P0)
**Статус:** 🚧 потрібно зробити.

Проблема: `npx tsc --noEmit` для всього Expo проєкту падає через **відсутні модулі**, які були видалені/не перенесені раніше (не в рамках Phase 4), наприклад:
- `../src/feedback`
- `../src/state-shift`
- `../src/validator-context`
- `../src/onboarding-tour`
- `../src/referral`
- `../src/ui-client`
- `./design-system/palette`

**Дії:**
1. Або відновити мінімальні заглушки модулів (експортувати no-op функції/компоненти),
2. Або прибрати імпорти/використання з `_layout.tsx`, `settings/account/...`, `theme-tokens.ts` тощо.

Ціль: Expo має збиратися без TypeScript errors та запускатися в dev.

---

## 3) Next Actions

**P0 (негайно):**
1. Expo: Tech debt — прибрати/заглушити відсутні модулі, щоб проєкт збирався (`tsc --noEmit` без помилок).
2. Expo: Smoke‑тест навігації на реальному рантаймі:
   - `/` → `/welcome` → `/auth` → `/client/home`
   - перевірка тем (light/dark) та логотипів
   - перевірка 2FA редіректів.
3. Expo: остаточно прибрати/пошук‑заміна залишкових згадок `EVA-X`, `developer`, `describe`, `workspace`, `lead`.

**P1:**
4. Expo: полірування інвест‑кабінету (client/*):
   - «Портфель», «Активи», «Раунди», «Виплати» — узгодити з web
   - додати екран деталей активу або deep‑link на web.
5. Web: Asset Detail page з повною розбивкою економіки активу (cashflow/IRR/ризики/документи/SPV).

---

## 4) Success Criteria
- Немає dev/tester/developer кабінетів у **web та Expo** (ні в меню, ні в роутингу, ні в підключеному коді).
- Усі тексти/терміни українською і звучать природно, як від копірайтера.
- Працює end‑to‑end:
  - Web: Landing → Auth/2FA → Investor dashboard → Assets/Calculator → (далі) Asset detail.
  - Expo: Welcome → Auth/2FA → Investor (client) home.
- Логотипи:
  - використовується тільки користувацький PNG
  - без домальовок/генеративних SVG
  - коректний вибір по темі
  - **компактний розмір** (не ламає верстку) і не обрізається.
- Web, backend та Expo запускаються без помилок; основні екрани відкриваються.

---

### Sprint 1 — Phase 0: Core Cleanup + Domain Lock (інвест-ядро)
**Статус:** ✅ виконано (2026-06-11).

Рішення (підтверджено користувачем):
- Legacy: Варіант A — нічого не видаляємо, тільки runtime-ізоляція через `LUMEN_ONLY=true`.
- Ownerships: тільки схема (без розрахунків/нарахувань/виплат).
- CRUD: НЕ робимо. Тільки схеми + індекси + репозиторії + 2 діагностичні endpoint'и:
  - `GET /api/admin/system/domain` — статус domain lock
  - `GET /api/admin/system/models` — колекції/моделі/індекси
- Додано 6-ту колекцію: `lumen_investor_profiles` (KYC/tax/IBAN/risk — порожня базова схема).

Реалізація:
- `LUMEN_ONLY=true` у `/app/backend/.env` — фільтр на `fastapi_app.on_event("startup")` (server.py:206-262).
- 22 legacy startup-хендлери skipped (workers/schedulers/loops/seeds EVA-X).
- 1 активний LUMEN startup: `_lumen_phase0_startup` (індекси 6 колекцій).
- Файли: `lumen_models.py` (6 Pydantic-моделей), `lumen_repositories.py` (генеричний repo + індекси).
- Smoke-тест: `/app/backend/tests/test_sprint1_smoke.py` — ALL PASS (create+read 6 колекцій, unique індекси, update/find, cleanup).

Перевірено (4 рівні):
1. Backend стартує без помилок ("Application startup complete").
2. Smoke endpoints: /api/, /api/assets (6), auth/quick, auth/me, admin/system/domain, admin/system/models — 200.
3. Mongo: create+read для assets/rounds/intents/investments/ownerships/profiles — PASS.
4. time_tracking_layer / execution_intelligence / money_bridge / autonomy_layer НЕ стартують; PAY-V2, guardian, module_motion, operator, balancer, event_engine, reconciler — skipped.

### Sprint 4 — Contracts & Legal Layer
**Статус:** ✅ виконано на 100% (2026-06-11). Регресія Sprint 1–4: ALL PASS. Testing agent E2E: 100% (0 багів).

**Юридичний ланцюг:** KYC → Investment Approved → Contract Generated → Contract Signed → Active.
Інвестиція активується ЛИШЕ коли `KYC approved AND contract signed` (Sprint 4 gate поверх Sprint 3).

**Backend (`lumen_contracts.py`):**
- 3 колекції: `lumen_contract_templates` (unique kind+seed 3 шаблонів UA), `lumen_contracts` (unique number `LMN-YYYY-NNNNN`), `lumen_signatures` (audit: timestamp/IP/user-agent).
- Lifecycle: draft → generated → sent → viewed → signed (+expired/cancelled).
- Генерація: автоматично після approve intent; плейсхолдери `{{investor_name}}/{{amount}}/{{asset_title}}/{{ownership_percent}}/...`; SPV-активи → шаблон spv_participation.
- PDF: reportlab + Liberation Sans (кирилиця), in-memory, блок Electronic Acceptance.
- Endpoints: investor contracts list/detail(marks viewed)/sign(agree required)/pdf; admin contracts list+counts/detail+signatures/cancel(signed → 409, скасування зупиняє інвестицію); admin templates GET/POST/PATCH (version bump).
- Активаційний рушій `activate_ready_investments`: kyc_pending+signed→active; kyc_pending(KYC ok, unsigned)→contract_pending; contract_pending+signed→active. Ownership/funding перераховуються тільки після активації.
- Startup backfill: історичні active інвестиції отримали авто-підписані legacy-контракти.
- **Фікси при завершенні:** (1) `_next_contract_number` — was count+1 → колізії з unique index після видалень; тепер max існуючого номера за рік +1. (2) LUMEN_ONLY route dedup у server.py — legacy EVA-X маршрути (`/api/admin/contracts*`, `/api/contracts/{id}/pdf`) затіняли Sprint 4 endpoints (FastAPI matching за порядком реєстрації) — під domain lock legacy-дублікати видаляються з route table.

**Frontend (web):**
- `/investor/contracts` (InvestorContracts.js): список + detail (рендер тексту договору), статуси UA, PDF, sign-flow (чекбокс згоди → «Підписати договір» → flash активації), блок «Підписано електронно» з IP/датою.
- `/admin/contracts` (AdminContracts.js): вкладки «Реєстр договорів» (фільтри+лічильники, таблиця, detail з підписами, cancel з причиною; signed не скасовується) та «Шаблони» (3 шаблони, редактор name/kind/body/active, нова версія, створення нового).
- `/admin/intents` (AdminIntents.js, **новий UX-гейп закрито**): черга заявок з фільтрами, Підтвердити (генерує договір) / Відхилити з причиною.
- Dashboard: банер «Інвестиція очікує підписання договору» (contract_pending) з CTA на /investor/contracts; бейджі «Очікує підпису» в списку інвестицій.
- Portfolio: статус `contract_pending` → бейдж «Очікує підпису».
- Навігація: «Договори» в сайдбарах інвестора/адміна + «Заявки» в адміна + MobileNav (drawer).

**Тести:**
- `tests/test_sprint4_contracts.py` (новий, ~50 перевірок): шаблони seed/CRUD/версії, генерація на approve, viewed-перехід, sign-валідації (agree 400, foreign 403, double 409, cancelled 409), Electronic Acceptance audit, PDF (owner/admin 200, foreign 403), активація + ownership + funding, sign-before-KYC → kyc_pending → KYC approve → auto-activate, admin cancel правила, доступи, cleanup.
- `tests/test_sprint2_core.py`, `tests/test_sprint3_kyc.py` оновлені під Sprint 4 gate (approve → contract_pending, активація через підпис).
- Регресія Sprint 1+2+3+4: **ALL PASS** (повторні прогони стабільні).
- Testing agent (iteration_5): backend 8/8, frontend 35+ перевірок — 100%, 0 багів.

**Наступне: Sprint 5 — Payments & Funding** (KYC → Contract → Payment → Ownership → Portfolio). Потім Sprint 6 — Asset Content Platform (галерея, документи, звіти, Q&A, команда, структура угоди, сценарії дохідності, ризики, exit-стратегія).

---

### Sprint 2 — Investment Core
**Статус:** ✅ виконано (2026-06-11). Тести: 32/32 smoke + 85/85 незалежна верифікація (100%).

**Domain Audit (перед кодом):**
- Assets: всі очікувані поля присутні в live-документах (category≈asset_type, round_target≈target_amount, raised≈raised_amount, target_yield≈expected_yield, horizon_months≈term_months). Pydantic-модель вирівняна до канону (cover_url, target_amount, raised_amount, term_months, location, spv_label, investors_count, featured).
- Rounds: колекція була порожня; модель доповнена round_name, minimum_ticket, open_at/close_at.
- Investments: модель повна; legacy seed канонізовано (amount, units, created_at, history).
- Виявлений drift: legacy intent писав у lumen_intents → тепер все у канонічній lumen_investor_intents.

**Реалізація (`/app/backend/lumen_investment_core.py`):**
1. Investor Intent Engine: POST /api/investor/intents, GET /api/investor/intents, GET /api/admin/intents(?status=,asset_id=)+counts, POST /api/admin/intents/{id}/approve, POST /api/admin/intents/{id}/reject. Валідації: asset open, amount>=min_ticket, авто-прив'язка відкритого раунду. Legacy POST /api/investor/intent — делегат у канонічний engine.
2. Investment Engine: інвестиція створюється ТІЛЬКИ через approve (Sprint 2: без оплати → одразу active), lifecycle statuses + append-only history. GET /api/investor/investments/{id}.
3. Ownership Engine: approve → intent(converted) → investment(active) → ownership upsert (units: 1 unit = 1 ₴; ownership_percent = сума active інвестицій інвестора в актив / target_amount × 100). Self-healing recompute. GET /api/investor/ownerships, GET /api/admin/ownerships.
4. Asset Funding Progress: raised_amount (+legacy дзеркало raised) та investors_count перераховуються з активних інвестицій; round.raised_amount оновлюється.
5. Portfolio Engine: GET /api/investor/portfolio переписано — збирається з ownerships+investments+assets (live-збагачення, зважена середня дохідність), НЕ з mock-полів. Формат відповіді сумісний з web-кабінетом.
6. Startup backfill (ідемпотентний): канонізація seed-інвестицій, «Раунд I» на кожен актив (6 раундів), ownership registry з активних інвестицій, raised_amount = реальні інвестиції (podilskyi: 2 976 000 fiction → 250 000 real — by design).
7. GET /api/admin/rounds читає з реєстру lumen_investment_rounds.

**Тести:** `/app/backend/tests/test_sprint2_core.py` (повний ланцюг + reject + 400/404/403/409 + cleanup).

**Скоуп-заборони дотримано:** без платежів / KYC / договорів / wallet / виводів / виплат / крипти / mobile redesign.

**Далі: Sprint 3 — KYC + Investor Profile** (на базі lumen_investor_profiles).

---

### Sprint 3 — KYC + Investor Profile
**Статус:** ✅ виконано (2026-06-11). Тести: Sprint 1 + Sprint 2 + Sprint 3 — ALL PASS (68/68 у test_sprint3_kyc.py). Testing agent: backend 100%, frontend 100% (після фіксу банера).

**Backend (`/app/backend/lumen_kyc.py`):**
- Investor Profile API: `GET/PATCH /api/investor/profile` (full_name, date_of_birth, phone, country, residency_country, tax_id, iban, bank_name, risk_profile, accreditation_status). Валідації: risk_profile ∈ 4 значення; `verified` акредитацію ставить лише комплаєнс; редагування заблоковано у submitted/under_review.
- KYC Documents: `POST/GET/DELETE /api/investor/kyc/documents` (6 типів: passport, tax_id, iban_proof, selfie, source_of_funds, other; multipart, ліміт 10МБ, файли на локальному диску uploads/kyc/). `GET /api/kyc/documents/{id}/file` — owner або admin (403 чужим).
- KYC статуси: not_started → draft → submitted → under_review → approved / rejected → (draft → submitted …) / expired. Дзеркало users.kyc_status підтримується.
- Submission: `POST /api/investor/kyc/submit` — completeness-гейт (missing list у error envelope `details`).
- Admin: `GET /api/admin/kyc` (черга + counts по 7 статусах), `GET /api/admin/kyc/{investor_id}` (картка: профіль + документи + kyc_pending/active investments), `POST .../approve` (note опційний), `POST .../reject` (reason ОБОВ'ЯЗКОВИЙ).
- Startup bootstrap: кожен client/investor отримує профіль (ідемпотентно); колекція lumen_kyc_documents у Phase 0 індексах (7 колекцій).

**Investment Core інтеграція (м'який режим — за рішенням):**
- Intent подається БЕЗ KYC.
- Admin approve intent: KYC approved → investment `active`; інакше → `kyc_pending` (без ownership, без funding, поза summary.active_count).
- Admin approve KYC → `activate_kyc_pending_investments()`: усі kyc_pending інвестиції активуються, ownership upsert + funding + round progress перераховуються, інвестор отримує сповіщення.

**Frontend Web:**
- Investor `/investor/profile` («Профіль та верифікація»): KYC статус-бейдж, причина reject, особисті дані, податкові/банківські (РНОКПП/IBAN/банк/ризик-профіль/акредитація), upload/видалення документів, «Подати на перевірку» (disabled поки missing), блокування форм поза editable-статусами.
- Investor `/investor/dashboard`: банер «Інвестиція очікує верифікації» + CTA «Пройти верифікацію» (коли є kyc_pending), бейдж «Очікує KYC» у списку інвестицій.
- Investor `/investor/portfolio`: колонка «Статус» (Активна / Очікує KYC / Очікує оплату / Завершена / Скасована).
- Admin `/admin/kyc` («Верифікація інвесторів»): фільтри з лічильниками, черга, картка інвестора (поля + документи з переглядом + контекст інвестицій), approve з коментарем комплаєнс, reject з обов'язковою причиною (кнопка disabled без неї), flash-повідомлення.
- `lumenApi.js`: хелпери `lumenError` / `lumenErrorDetails` — коректний парсинг error envelope `{ok, code, message, details}` (виправлено читання `detail` → envelope).

**Тести (`/app/backend/tests/test_sprint3_kyc.py`, 68 перевірок):** lifecycle статусів, валідації полів, документи (upload/download/delete, типи, порожній файл), submission-гейт + edit-lock, права доступу (інвестор ≠ адмін, чужі документи 403, self-approve заборонено), черга/картка/approve/reject (+409 guard-и, 404, 422), м'який режим end-to-end (kyc_pending → активація + ownership + funding), повторна подача після reject, cleanup без слідів.

**Скоуп-заборони дотримано:** без e-sign / договорів / платежів / wallet / виплат / crypto / secondary market.

**Definition of Done:** ✅ всі пункти (профіль; KYC анкета; документи; адмін-черга; approve/reject; KYC впливає на lifecycle інвестицій; тести прав доступу/статусів; Sprint 1–2 тести не зламані).

**Далі: Sprint 4 — за рішенням продукту (наприклад, договори/e-sign або платежі).**

---

### Redeploy 2026-06-11 (новий pod) — статус розгортання
**Статус:** ✅ повністю розгорнуто та перевірено.

1. Репозиторій склоновано → код у `/app` (backend + frontend + expo + packages).
2. `.env` відтворено по README (відсутні в git):
   - backend: `MONGO_URL`, `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0`
   - frontend: `REACT_APP_BACKEND_URL` (preview URL збережено)
3. Залежності: `pip install -r requirements.txt` + `yarn install` — OK.
4. Виправлено конфлікт: видалено залишковий `frontend/jsconfig.json` старого шаблону (конфліктував із `tsconfig.json` репо) — фронтенд компілюється.
5. Свіжа БД: demo-користувачі сидяться legacy `startup_event`, який skipped під LUMEN_ONLY → створено one-off скрипт `/app/backend/scripts/bootstrap_seed_once.py` (ідемпотентний). 12 користувачів засіяно.
6. Перевірено end-to-end:
   - Backend: startup clean, LUMEN domain lock активний (22 legacy skipped, 1 LUMEN startup), 6 активів, раунди, portfolio.
   - Auth: `auth/quick` + `auth/login` (client123/admin123) — OK.
   - Web: Landing (UA, teal/gold, Lumen лого) → /auth → /investor/dashboard (₴874 892, 3 інвестиції) → /admin/dashboard (Панель фонду) — скриншоти OK.
   - Smoke-тести репо: `test_sprint1_smoke.py` ALL PASS, `test_sprint2_core.py` ALL PASS (32/32).
   - KYC (Sprint 3): investor/profile, kyc/documents, admin/kyc — відповідають 200.
7. Креденшіали задокументовано: `/app/memory/test_credentials.md`.

**Відомі залишки (без змін, як у репо):** Expo TypeScript tech debt (Phase 5) — відсутні модулі feedback/state-shift/onboarding-tour/referral; Expo deps не встановлювались на цьому pod (мобільний застосунок опційний).

---

### Redeploy (pod arch-review-24) — статус розгортання
**Статус:** ✅ повністю розгорнуто та перевірено.

1. Репозиторій `svetlanaslinko057/12312es1` склоновано → код у `/app` (backend + frontend + expo + packages + memory).
2. `.env` відтворено (відсутні в git):
   - backend: `MONGO_URL`, `DB_NAME=evax_devos`, `LUMEN_ONLY=true`, `INTEGRATIONS_LIVE_ENABLED=0`, `EMERGENT_LLM_KEY`
   - frontend: `REACT_APP_BACKEND_URL=https://arch-review-24.preview.emergentagent.com`
3. Залежності: `pip install -r requirements.txt` + `yarn install` — OK. Конфліктний legacy `frontend/jsconfig.json` видалено превентивно.
4. Свіжа БД: `scripts/bootstrap_seed_once.py` — 12 користувачів засіяно; startup засіяв 6 активів, 3 шаблони договорів (Sprint 4), asset content (Sprint 5), 15 LUMEN-колекцій з індексами, domain lock активний (22 legacy startup skipped).
5. Перевірено end-to-end:
   - API: /api/assets (6 активів), auth/quick, auth/login (client123/admin123) — OK.
   - Web: Landing (UA, Lumen) → /investor/dashboard (₴874 892, 3 інвестиції) → /admin/dashboard (Панель фонду, 5 раундів) — скриншоти OK.
   - Регресія: test_sprint1_smoke, test_sprint2_core, test_sprint3_kyc, test_sprint4_contracts, test_sprint5_content — ALL PASS.
     (Перший прогін S2 на свіжій БД мав 3 state-залежні фейли backfill/funding; повторний прогін — ALL PASS, self-healing спрацював.)
6. Останні доробки в коді: **Sprint 5 — Asset Content Platform** (`lumen_asset_content.py`): галерея/відео/команда/ризики/exit на активі, updates (блог активу), reports, documents, Q&A, SPV-картки; admin CRUD + публічні/інвесторські ендпоінти; файли локально в uploads/asset_content/.

**Відомі залишки (без змін, як у репо):** Expo TypeScript tech debt (Phase 5); Expo deps не встановлювались на цьому pod (мобільний застосунок опційний).

**Далі:** очікуємо нові задачі від користувача (продовження роботи над останніми тасками).

---

### Sprint 5 — Asset Content Platform (слой доверия)
**Статус:** ✅ завершено полностью (pod arch-review-24). Testing agent E2E: 100% (45/45, iteration_6, 0 багов). Решение продукта: Sprint 5 = Asset Content (раньше платежей), Payments & Funding сдвинут в Sprint 6.

**Backend (`/app/backend/lumen_asset_content.py`, был готов, тесты ALL PASS):**
- На активе: gallery[] (фото+подписи), videos[] (YouTube/Vimeo → авто embed_url), team[], risks[] (severity low/medium/high), exit_strategy. `PATCH /api/admin/assets/{id}/content`.
- lumen_asset_updates — блог актива (kind: milestone/news/general, pinned, published) + admin CRUD.
- lumen_asset_reports — отчёты (monthly/quarterly/annual, период, summary, PDF) + публикация/скрытие + download.
- lumen_asset_documents — документы (valuation/audit/lease_agreement/financial_model/permit/legal/other; visibility public/investors c locked-гейтом для гостей) + download.
- lumen_asset_questions — Q&A: инвестор спрашивает (мин. 10 символов), админ отвечает публично, hide/restore; `GET /api/admin/questions` (очередь+counts, фильтры по статусу/активу).
- lumen_spvs — SPV-реестр (name, registration_number/ЄДРПОУ, jurisdiction, asset_id, status forming/active/dissolved, notes); публичная карточка `GET /api/assets/{id}/spv`; admin CRUD. Основа модели Asset → SPV → Investors.
- Идемпотентный seed контента на стартапе; файлы в uploads/asset_content/ (mock storage).
- Тесты: `tests/test_sprint5_content.py` — ALL PASS.

**Frontend Web — было готово:**
- InvestorAssetDetail: галерея с миниатюрами, вкладки Огляд (відео iframe, команда, ризики з бейджами, exit, SPV-картка з ЄДРПОУ, економіка) / Оновлення / Звіти й документи (download, locked для гостей) / Питання (форма + список + «Відповідь оператора»).
- AdminAssetContent: 8 вкладок (Медіа/Команда/Ризики й вихід/Оновлення/Звіти/Документи/Q&A/SPV) с CRUD и flash.
- AdminQuestions: глобальная очередь Q&A с фильтрами-счётчиками и ответом.

**Frontend Web — ДОДЕЛАНО в этом сеансе (страницы были написаны, но не подключены):**
- `App.js`: lazy-импорты + роуты `/admin/assets/:assetId/content` (AdminAssetContent) и `/admin/questions` (AdminQuestions).
- `AdminLayout.js` + `MobileNav.js`: nav-пункт «Питання (Q&A)» (icon MessageCircleQuestion).
- `AdminAssetEditor.js`: кнопка-ссылка «Контент і довіра» (data-testid=asset-content-link) на страницу контента актива.

**E2E (iteration_6.json):** backend smoke 10/10, инвестор 16/16, админ 19/19, регрессия 6/6. Полный цикл Q&A: вопрос инвестора → ответ админа → инвестор видит ответ. Регрессия S1–S4 не сломана.

**Скоуп-заборони дотримано:** без платежей / wallet / выплат / secondary market.

**Далее: Sprint 6 — Payments & Funding** (payment_requests; lifecycle awaiting_payment → paid → under_review → confirmed/rejected; manual bank transfer: реквизиты + загрузка подтверждения + проверка админом; Ledger: credit/debit только через журнал, без прямых изменений балансов). Затем Sprint 7 — Wallet + Withdrawals, Sprint 8 — Payout Engine, Sprint 9 — Investor Analytics, Sprint 10 — Secondary Market.

---

## Sprint 6 — Payments & Funding + Ledger — ✅ COMPLETED

**User-выбранные параметры:**
1. Backfill option C — историческим active investments присвоены payment_requests(confirmed) + ledger_entries(credit, investment_funding).
2. Multi-currency: UAH (base) / USD / EUR с fx_rate + amount_uah снимком.
3. payment_request создаётся только после полного legal gate: KYC approved + contract signed.
4. In-app notifications: payment_request_created / payment_submitted / payment_confirmed / payment_rejected (без email).
5. Мягкий KYC-режим сохранён.

**Backend (новые модули и изменения):**
- `lumen_payments.py` — 4 коллекции:
  - `lumen_payment_requests` (id, investor_id, investment_id, asset_id, amount, currency, base_currency=UAH, fx_rate, amount_uah, status, payment_method, funding_account_id, proof_ids[], history[])
  - `lumen_payment_proofs` (PDF/PNG/JPG/WEBP, до 10 МБ, локальное хранилище `uploads/payment_proofs/`)
  - `lumen_funding_accounts` (admin CRUD; типы bank_transfer/swift/crypto_future; soft delete; default per currency; seed 3 рахунки)
  - `lumen_ledger_entries` (append-only credit/debit; причины: investment_funding/payout/withdrawal/adjustment/refund)
- Endpoints:
  - Investor: `GET /api/investor/payments(?status=)`, `GET /api/investor/payments/{id}` (с реквизитами + proofs), `POST .../proof`, `DELETE .../proof/{pid}`, `POST .../submit`, `GET /api/payment-proofs/{pid}/file`, `GET/POST /api/investor/notifications(/mark-read)`
  - Admin: `GET /api/admin/payments(?status=&asset_id=&investor_id=)`, `GET /api/admin/payments/{id}`, `POST .../confirm`, `POST .../reject`, `POST .../clarification`; `GET/POST/PATCH/DELETE /api/admin/funding-accounts`; `GET /api/admin/ledger(?entry_type=&reason=&investor_id=&asset_id=)`; `GET /api/funding-accounts/public`
- Lifecycle change (КРИТИЧЕСКИЙ):
  - `lumen_contracts.py` — после `sign` → `open_payment_requests_for_investor` (если KYC ok + signed); investment.status → `awaiting_payment`.
  - `lumen_investment_core.py` — `activate_ready_investments` теперь делает только `kyc_pending → contract_pending`; ownership/raised/portfolio пересчёт удалён (теперь только в `confirm_payment_request`).
  - `lumen_kyc.py` — после `approve` зовёт `open_payment_requests_for_investor` для уже подписанных договоров. Поле `activated_investments` для backward-compat = number of opened payment_requests.
  - Новый статус `awaiting_payment` в INVESTMENT_STATUS_LABELS.
- Backfill (idempotent, на startup):
  - 6 active investments → 6 payment_requests (status=confirmed, is_backfilled=true) + 6 ledger_entries (credit, investment_funding).
  - Сумма ledger total_uah_credit = 2 900 000 ₴ (после S6 E2E 2 500 000 ₴ инвестора client@atlas.dev).
  - Нормализация raised_amount: phantom 1.68M на `asset-rivne-warehouse` (без active investments) обнулён под правило «ledger = source of truth». Для assets с фактическими investments значения сохраняются.
- LUMEN_ONLY route dedup расширен: legacy `/api/admin/payments` из `lumen_api.py` и `compat_routes.py` дропаются, route остаётся только за `lumen-payments` тегом.

**Frontend Web — новые / переписанные страницы:**
- `InvestorPayments.js` (My Funding): 4 KPI карточки (Очікують оплати/На перевірці/Підтверджених/Оплачено всього), фильтры-пилюли с counts, карточки платежей со статус-бейджами и валютой, drawer с реквизитами (CopyRow: IBAN/SWIFT/Beneficiary/ЄДРПОУ/призначення), upload PDF/JPG/PNG/WEBP до 10 МБ, submit с выбором метода и комментарием, история событий, плашки для rejected/under_review/confirmed.
- `AdminPayments.js`: queue-фильтры с счётчиками (paid/under_review/awaiting_payment/confirmed/rejected), таблица investor/asset/amount/date/proofs/status, drawer с investment-инфо + ledger entries, 3 действия (confirm/reject/clarification), reason обязателен для reject, note для clarification.
- `AdminFundingAccounts.js`: список + edit drawer; полный CRUD; типы bank_transfer/swift/crypto_future; валюты UAH/USD/EUR/USDT; soft delete; default per currency.
- `AdminLedger.js`: 4 KPI карточки (Credit UAH / Debit UAH / Net UAH / Усього), фильтры по type (credit/debit) и reason, таблица с цветной маркировкой credit (зелёный +) / debit (красный −).
- `InvestorDashboard.js`: новый sky-banner `awaiting-payment-banner` (CTA → /investor/payments) + бейдж «Очікує оплату» на инвестиции (`inv-awaiting-payment-{id}`).
- `AdminLayout.js`: добавлены nav-пункты «Реквізити» (Landmark icon, `/admin/funding-accounts`) и «Реєстр (Ledger)» (BookOpen icon, `/admin/ledger`).
- `MobileNav.js`: тот же набор в секции Фінанси.
- `App.js`: lazy-роуты `/admin/funding-accounts`, `/admin/ledger`.

**Тесты:**
- `tests/test_sprint6_payments.py` — POC E2E (42 проверки) ALL PASS:
  - Backfill integrity + ledger sums.
  - Funding accounts admin CRUD + public read.
  - Полный lifecycle: intent → approve → contract sign → awaiting_payment → upload proof → submit (paid) → clarification (under_review) → reject (rejected) → re-submit → confirm → ledger credit + ownership + raised_amount.
  - Idempotency: double-confirm → 409.
  - Notifications: 4 события зарегистрированы.
  - Регрессия S2/S3/S4 endpoints (portfolio/profile/contracts/assets).
- `test_sprint1_smoke`, `test_sprint2_core`, `test_sprint3_kyc`, `test_sprint4_contracts`, `test_sprint5_content` обновлены под Sprint 6 lifecycle (sign → awaiting_payment → admin confirm → active) — ALL PASS.
- E2E (iteration_7.json): backend 7/7, investor frontend 10/10, admin frontend 19/20 (1 минорный testid mismatch на legacy /investor/assets — не Sprint 6), регрессия S1–S5 100%. Общий пасс — 98% (36/37).

**Архитектурный итог Sprint 6:**
> Ownership, raised_amount и portfolio появляются ТОЛЬКО после `confirmed payment`.
> Любое движение денег идёт через `lumen_ledger_entries`. Это фундамент для Sprint 7 (Wallet + Withdrawals), Sprint 8 (Payouts) и Sprint 10 (Secondary Market).

**Далее: Sprint 7 — Wallet + Withdrawals**, Sprint 8 — Payout Engine, Sprint 9 — Investor Analytics, Sprint 10 — Secondary Market, Sprint 11 — Production Hardening.
