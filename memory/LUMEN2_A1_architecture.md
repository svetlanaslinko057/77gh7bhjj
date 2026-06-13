# LUMEN 2.0 — Master Roadmap & Phase A1 Architecture

> Зафіксовано як джерело істини для всіх наступних фаз. LUMEN перестає бути
> "real-estate crowdfunding" і стає **Asset Marketplace** (Republic-style).

## Master Roadmap (фази)

| Фаза | Назва | Суть | Статус |
|------|-------|------|--------|
| **A** | Ownership OS | Фундамент володіння: integer units, сертифікати, lifecycle | **A1/A2/A3 DONE** |
| **B** | Asset Marketplace 2.0 | Investment Thesis, Scenario Engine, Capital Stack, Asset Journal, Live Metrics, Conviction/Liquidity Score, Similar Assets | **DONE (B1–B8)** |
| C | Community OS | Discussion Board, Voting (голосують units), Activity Feed | **DONE (C1–C7)** |
| D | Secondary Market 2.0 | Order Book (BID/ASK), Partial Fill, Market Data, Liquidity, OTC | pending |
| E | Portfolio OS | Allocation, Health (diversification/concentration), Goals | pending |
| F | Payment Rails 2.0 | USDT rail (тільки ввід), Auto Conversion, Multi-Currency | pending |
| G | Issuer OS | Кабінет емітента (звіти/фото/оновлення/виплати) | pending |
| H | Republic Layer | Категорії активів: Real Estate / Solar / Agriculture / Warehouse / Parking / Private Business | pending |

---

## Phase B — Asset Marketplace 2.0 (IMPLEMENTED — Asset Intelligence Layer)

### Принцип
Після A3 контур володіння закритий (купити/обліковувати/виплачувати/перепродати).
Слабке місце — *переконати* інвестора купити саме цей об'єкт. Phase B перетворює
статичну картку на живий організм. Усі числа деривуються з реальних колекцій —
жодних моків. Один спроєктований шар, не B1 окремо.

### Файли / колекції
- Engine + API: `backend/lumen_asset_intelligence.py` (router prefix `/api`, wired у server.py + startup seed `seed_intelligence_demo`).
- Авторський контент зберігається на `lumen_assets`: `thesis{opportunity,market,execution,exit}`, `capital_stack{asset_value,debt,platform,investors,reserve}`, `occupancy_percent`, `scenario_factors{bear|base|bull:{yield_factor,exit_factor}}`, `journal_milestones[]`.
- Деривовані дані читаються з: `lumen_payout_records` (виплати), `lumen_secondary_listings/bids/trades` (ліквідність), `lumen_ownerships` (власники + avg hold), `lumen_asset_reports`/`lumen_asset_updates` (прозорість/journal).

### Блоки
- **B1 Investment Thesis** — авторські 4 поля (Opportunity/Market/Execution/Exit).
- **B2 Scenario Engine** — Bear/Base/Bull, обчислюються з власної економіки активу (множники yield/exit; Base=1.0). Гібрид: дефолти + admin override через `scenario_factors`.
- **B3 Capital Stack** — водоспад (debt/platform/investors/reserve) + % + investor_share. Авторський; fallback-дериватив якщо не заповнено.
- **B4 Asset Journal** — авторські віхи MERGE з реальними подіями (публікація, закриття раунду, звіти, оновлення, виплати, угоди вторинки), сорт desc.
- **B5 Live Metrics** — funding progress, investor_count, secondary liquidity, avg hold days, payout history, occupancy.
- **B6 Conviction Score (0..100)** — детермінований з фактів (payout_consistency 0.30, occupancy 0.25, report_frequency 0.20, yield_history 0.15, funding 0.10). НЕ AI. band low/medium/high.
- **B7 Liquidity Score (0..10)** — supply (listings) + demand (bids) + activity (trades 90d) + breadth (holders). band low/medium/high.
- **B8 Similar Assets** — та сама категорія, ранжування за близькістю дохідності.

### API
- Public/investor: `GET /api/assets/{id}/intelligence|scenarios|capital-stack|journal|metrics|conviction|liquidity|similar`
- Admin: `GET /api/admin/assets/{id}/intelligence`, `PATCH /api/admin/assets/{id}/intelligence` (thesis/capital_stack/occupancy/scenario_factors), `GET/POST /api/admin/assets/{id}/journal`, `DELETE /api/admin/asset-journal/{milestone_id}`

### Frontend
- Спільні компоненти: `src/components/lumen/AssetIntelligence.js` (IntelligencePanel, InvestmentThesis, ScenarioEngine, CapitalStack, AssetJournal, SimilarAssets, ConvictionBadge/LiquidityBadge/AssetScoreBadges, useAssetIntelligence).
- Investor `pages/investor/InvestorAssetDetail.js` — блоки B1/B2/B3/B5/B6/B7 у вкладці «Огляд», нова вкладка «Шлях активу» (B4), «Схожі об'єкти» (B8), бейджі у заголовку.
- Public `pages/PublicAssetDetail.js` — той самий досвід без auth (basePath `/objects`).
- Cards: `pages/investor/InvestorOpportunities.js` — `AssetScoreBadges` (conviction+liquidity) на картках.
- Admin authoring: `pages/admin/AdminAssetContent.js` — вкладка «Marketplace 2.0» (thesis/capital stack/occupancy/scenario factors/journal milestones).

### Тести (iteration_4.json)
- Backend 32/33 ✅ (1 transient 502, не баг). Frontend 100% ✅. 0 critical/UI/integration issues.
- Демо-сід: 5 активів збагачено thesis+capital_stack+occupancy+milestones на старті (ідемпотентно).

---

## Phase C — Ownership Community OS (IMPLEMENTED)

### Принцип
Поворот після B: головний дефіцит LUMEN — не торгівля долями, а *причина повертатися*
між купівлею і продажем. Community OS закриває це. Це НЕ форум/соцмережа — спільнота
будується НАВКОЛО конкретного активу і гейтиться реальним володінням (units з
`lumen_ownerships`). Усе деривується з реальних даних.

### Файли / колекції
- Engine + API: `backend/lumen_community.py` (router prefix `/api`, wired у server.py + startup `ensure_community_indexes` + `seed_community_demo`).
- Колекції: `lumen_community_posts` (discussion|question|announcement), `lumen_community_comments`, `lumen_community_polls`, `lumen_community_ballots` (unique poll+voter, зберігає units_weight), `lumen_community_sentiment` (unique asset+holder mood pulse).
- Гейтинг: `_units_of(asset_id, uid)` з `lumen_ownerships`; admin bypass.

### Блоки
- **C1 Asset Feed** — стрічка на актив: оголошення + питання + обговорення (не глобальна).
- **C2 Ownership Lounge** — units-gated: маєш units → бачиш/постиш holders-only обговорення.
- **C3 Questions 2.0** — питання → відповідь оператора → коментарі інвесторів (обговорення).
- **C4 Voting** — опитування, ВАГА = units власника (рекомендаційне, не юридичне). Ballot upsert per voter, snapshot units_weight.
- **C5 Asset Sentiment** — mood pulse власника (positive/neutral/negative), зважений по units → positive/neutral/negative %. Без AI.
- **C6 Reputation** — per-asset (НЕ глобальна карма): score = posts·5 + comments·2 + votes·3 + pulse·1 + reactions_received·1 → tiers Спостерігач/Учасник/Активний/Лідер.
- **C7 Announcements** — оператор публікує (орендар/ремонт/звіт/виплата) → нотифікації всім власникам (`lumen_notifications`).

### API
- Public/holder: `GET /api/assets/{id}/community/summary|feed|polls|leaderboard`, `GET /api/community/posts/{post_id}`
- Auth: `POST /api/assets/{id}/community/posts` (discussion=holder, question=any), `/posts/{id}/comments`, `/posts/{id}/react`, `/comments/{id}/react`, `POST /api/assets/{id}/community/sentiment`, `POST /api/community/polls/{id}/vote`
- Admin: `POST /api/admin/assets/{id}/community/announcements` (notifies holders), `POST .../community/polls`, `POST /api/admin/community/polls/{id}/close`, `POST /api/admin/community/posts/{id}/answer|pin`, `DELETE /api/admin/community/posts/{id}`, `DELETE /api/admin/community/comments/{id}`

### Frontend
- Компонент: `src/components/lumen/AssetCommunity.js` (sentiment bar, mood selector, sub-nav Стрічка/Lounge/Голосування/Рейтинг, PostCard з реакціями+коментарями+відповіддю оператора, PollCard з unit-weighted результатами, Composer, Leaderboard).
- Вкладка «Спільнота» на `InvestorAssetDetail.js` (holder-досвід) і `PublicAssetDetail.js` (anon бачить публічне + login prompt, lounge заблокований).
- Admin: `AdminAssetContent.js` вкладка «Спільнота» — оголошення (C7), створення/закриття опитувань (C4), модерація (answer/pin/hide).
- Нотифікації від C7/коментарів падають у наявну сторінку нотифікацій інвестора.

### Тести (iteration_5.json)
- Backend 20/21 ✅ (1 «fail» = login rate-limit, очікувано). Frontend 100% ✅. 0 critical/UI/integration issues.
- Перевірено: гейтинг (anon 401/403, non-holder 403), unit-weighted voting, sentiment, reputation/leaderboard, оголошення→нотифікації, відповідь/pin/hide оператора.
- Демо-сід: оголошення + lounge-обговорення + опитування + mood pulses на реальних власниках (ідемпотентно).

---


## Phase A — Ownership OS

- **A1. Unit Registry Engine** ✅ DONE
- **A2. Certificate Engine** ✅ DONE
- **A3. Ownership Lifecycle** ✅ DONE (this sprint)

---

## A3 — Ownership Lifecycle (IMPLEMENTED)

### Принцип
Замикає розрив між покупкою і сертифікатом: канонічний, повністю трасований
ланцюг володіння. Source of truth лишається розподіленим по реальних сутностях;
A3 **деривує** канонічний lifecycle (не дублює істину).

Канонічний ланцюг:
`Intent → KYC → Contract → Payment → Funding → Ownership Created → Certificate Issued → Active → Payouts → Withdrawal`

### Файли / колекції
- Engine: `backend/lumen_ownership_lifecycle.py`
- Колекція: `lumen_lifecycle_events` (зміни канонічного стану)
- Поля: `lumen_investments.lifecycle_state`; `lumen_ownerships.certificate_id/certificate_number` (binding); `lumen_ownership_events.kind` (canonical); `lumen_certificate_events` нові типи.
- Hooks у `_settle_trade`: 6c cert burn&reissue → 6d `lifecycle.bind_all()` (rebind).
- Startup: `reconcile_all()` (binding + canonical state) після A2.

### Блоки
- **B1 Certificate Binding** — обов'язковий `ownership_id ↔ certificate_id` (двосторонній). `bind_all()` ідемпотентний.
- **B2 Lifecycle Engine** — канонічна машина станів (10 станів) деривується з intent/kyc-profile/contract/payment_request/ownership/certificate/payouts/withdrawal.
- **B3 Canonical ownership kinds** — `lumen_ownership_events.kind`: created/increased/decreased/transferred/closed.
- **B4 Certificate ownership events** — ownership_created/ownership_closed (reconcile) + ownership_split/ownership_merge (secondary). ✅ підтверджено: trade-hook емітить split+merge+transferred.
- **B5 Portfolio Timeline 2.0** — 8 кроків інвестора: Заявка/KYC/Договір/Оплата/Сертифікат/Активна/Перша виплата/Виведення доходу.
- **B6 Ownership Explorer** — повна трасировка: investment→payment→ledger→ownership→certificate→payouts→secondary→ownership_events.

### API
- Investor: `GET /api/investor/lifecycle`, `GET /api/investor/lifecycle/{investment_id}`
- Admin: `GET /api/admin/ownership/trace?investor_id=&asset_id=`, `GET /api/admin/ownership/{ownership_id}/trace`, `GET /api/admin/lifecycle/states`, `POST /api/admin/lifecycle/reconcile`

### Frontend
- Investor `pages/investor/InvestorJourney.js` → `/investor/journey` (nav "Шлях інвестицій") — expandable cards + vertical 8-step timeline.
- Admin: trace drawer у `pages/admin/AdminUnitRegistry.js` (кнопка "Trace" у cap table) — canonical-path chips + 7 секцій трасування.

### Тести (iteration_3.json + ручна перевірка)
- Backend 28/28 ✅, Frontend UI verified. Ручна перевірка trade-hook: емітовано ownership_split + ownership_merge + transferred; A1 invariants all_ok=true; A2 invariants all_ok=true; binding intact.

---

## (A1/A2 нижче)

---

## A2 — Certificate Engine (IMPLEMENTED)

### Принцип
Сертифікат **НЕ** source of truth. Source of truth = unit registry (A1).
Сертифікат — юридичний/користувацький артефакт, що **звіряється** з реєстром:
`ownership.units_int → active certificate`.

### Lifecycle (burn & re-issue)
- новий власник / перші units → **issue** (active, подія `issued`)
- units змінились (top-up / вторинка) → старий → `replaced`, новий → `active` (`reissued`)
- units → 0 (продав усе) → старий → `voided`
- ручні: admin void / admin reissue

### Файли / колекції
- Engine: `backend/lumen_certificates.py`
- Колекції: `lumen_certificates`, `lumen_certificate_events` (append-only), `lumen_certificate_templates`, `lumen_counters` (atomic № `LMN-YYYY-NNNNNN`)
- Hook: `lumen_secondary._settle_trade` крок 6c → `certificates.on_trade_settled` (після 6b registry-хука)
- Startup: ідемпотентний `reconcile_all()` (після A1 міграції)
- PDF: reportlab; QR: qrcode → public verify URL (`PUBLIC_BASE_URL`/forwarded headers)

### Статуси
`active` / `replaced` / `voided` / `expired` / `draft` (issued — транзитний)

### Поля сертифіката
certificate_number, verify_code (унікальний), investor_id/name, asset_id/title,
spv_id/spv_name, units (int), total_units, ownership_percent, unit_price_uah,
value_uah, issue_date, status, linked_contract_id, parent_certificate_id, replaced_by.

### Інваріанти A2 (all_ok=true)
- `active cert units == registry units_int`
- `single active per (investor, asset)`
- `every active ownership (units>0) has active cert`
- `verify_code unique`
- A1 registry-інваріанти лишаються green після всіх A2-операцій ✅

### API
- Public (no auth): `GET /api/public/certificates/verify/{code}` — **без приватних даних** (немає investor_id/name)
- Investor: `GET /api/investor/certificates`, `/{id}`, `/{id}/pdf`
- Admin: `GET /api/admin/certificates` (filter status/asset/investor), `/{id}`, `/{id}/pdf`,
  `POST /{id}/void`, `POST /{id}/reissue`, `POST /reconcile`, `GET /invariants/check`

### Frontend
- Investor `pages/investor/InvestorCertificates.js` → `/investor/certificates` (nav "Сертифікати") — active+history, PDF, Перевірити, Історія drawer.
- Admin `pages/admin/AdminCertificates.js` → `/admin/certificates` (nav "Сертифікати") — counts + invariants pill + Звірити + filters/search + detail drawer (audit + Перевипустити/Анулювати/PDF).
- Public `pages/CertificateVerifyPage.js` → `/certificates/verify/:code` (no auth) — valid/invalid card, privacy note.

### Тести (iteration_2.json)
- Backend 11/11 ✅, Frontend 3/3 ✅, overall 100%, 0 issues. Burn & re-issue verified, public verify privacy-safe, A1+A2 invariants green.

### НЕ робили (за вимогою): NFT, blockchain, crypto token, external e-sign, нотаріат, податкові звіти.

---

## (A1 нижче)


---

## A1 — Unit Registry & Ownership OS (IMPLEMENTED)

### Зафіксовані рішення (10 питань)
1. Що купує інвестор → **Investment Certificate, обеспечений integer units доли SPV** (екон. права).
2. Дроблення → **integer base-unit**, фіксований `total_units` (default 100 000) на актив.
3. Мін. лот → одиниця (units), майбутній `min_lot_units` per asset (Phase D).
4. Консолідація → авто (агрегована ownership-строка на (investor, asset)).
5. Вторинка → ціль **order book (стакан)**; A1 фіксує integer-реєстр під це.
6. При продажу → **burn & re-issue** сертифіката (append-only events) — реалізується в A2.
7. SPV → **1 на актив** (`LumenSpv.asset_id`).
8. Права → **економічні** (дохід оренди + продаж), без управлінського контролю.
9. USDT → **спосіб поповнення**; володіння завжди в UAH (кошик уже мультивалютний).
10. Сертифікат → № + інвестор + SPV + актив + units + % + дата + QR + статус (A2).

### Модель
- `unit_price_uah = target_amount / total_units`
- `units_int = owned_uah / unit_price` (derived) — **largest-remainder** гарантує
  `Σ holder.units == issued_units ≤ total_units`.
- Cap table авторитетно = active `lumen_investments` ± `lumen_share_transfers`.
- **НЕ змінює** legacy float `units`/`ownership_percent` → payouts (percent) і
  secondary (amount_uah) працюють без змін. `units_int` матеріалізується на
  ownership-рядках для швидкого читання.

### Файли / колекції
- Engine: `backend/lumen_unit_registry.py`
- Колекції: `lumen_asset_units`, `lumen_ownership_events` (append-only), `lumen_ownership_snapshots`
- Hook: `lumen_secondary._settle_trade` → `on_trade_settled` (emit transfer_in/out + recompute)
- Startup: ідемпотентна `migrate_all(emit_genesis=True)` в `server.py`

### API
- Admin: `GET /api/admin/registry/summary`, `/invariants`, `/asset/{id}`, `/asset/{id}/events`,
  `/asset/{id}/snapshots`, `POST /asset/{id}/snapshot`, `POST /asset/{id}/recompute`, `POST /migrate`
- Investor: `GET /api/investor/units`, `GET /api/investor/units/{asset_id}/events`

### Frontend
- Admin: `pages/admin/AdminUnitRegistry.js` → `/admin/registry` (nav "Реєстр одиниць")
  — Dashboard (Total/Issued/Listed/Available + asset cards) + Ownership Explorer (cap table + event stream + snapshot/recompute + invariant badge).
- Investor: `pages/investor/InvestorUnits.js` → `/investor/units` (nav "Мої частки")
  — Summary + per-asset holdings (units/%/value) + Історія drawer.

### Тести (iteration_1.json)
- Backend 18/18 ✅ (incl. secondary-transfer conservation). Frontend 100% ✅. 0 issues.
- Migration: 6 assets, `all_invariants_ok=true`. Total 600 000 units, issued 17 612.

### Forward-compat для A2 (Certificate Engine)
- `lumen_ownership_events` уже несе поле `certificate_id` (зараз null) — A2 чіпляє сертифікати на події без міграції.
