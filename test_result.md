#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================
## user_problem_statement: "LUMEN 2.0 / Phase A3 — Ownership Lifecycle. Close the gap between purchase and certificate by making the ownership chain canonical & traceable: Intent→KYC→Contract→Payment→Funding→Ownership Created→Certificate Issued→Active→Payouts→Withdrawal. Block1 Certificate Binding (mandatory ownership_id<->certificate_id). Block2 Lifecycle Engine (canonical state machine derived from real entities). Block3 canonical ownership event kinds (created/increased/decreased/transferred/closed). Block4 certificate events (ownership_created/closed/split/merge). Block5 Portfolio Timeline 2.0 (investor 8-step journey). Block6 Ownership Explorer (admin full trace: investment→payment→ledger→ownership→certificate→payouts→secondary). A1 + A2 invariants must remain green."

backend:
  - task: "A3 Lifecycle Engine + canonical state + investor timeline"
    implemented: true
    working: true
    file: "lumen_ownership_lifecycle.py, server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Startup reconcile binds certs + sets lifecycle_state. GET /api/admin/lifecycle/states → 3 active. GET /api/investor/lifecycle (client@atlas.dev) → 3 investments, each canonical_state=active, 7/8 steps done (withdrawal pending), correct 8-step timeline (intent/kyc/contract/payment/certificate/active/first_payout/withdrawal). GET /api/investor/lifecycle/{id} detail works. Verified via curl."
  - task: "A3 Block1 Certificate Binding (ownership_id <-> certificate_id)"
    implemented: true
    working: true
    file: "lumen_ownership_lifecycle.py, lumen_secondary.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "bind_all() links active certs to ownership rows both ways. Verified: ownership.certificate_number=LMN-2026-000003 present in trace. Re-bind hook (6d) runs after secondary settlement."
  - task: "A3 Block6 Ownership Explorer trace API"
    implemented: true
    working: true
    file: "lumen_ownership_lifecycle.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/admin/ownership/trace?investor_id=&asset_id= returns full trace: ownership (certificate_number bound), lifecycle, investments(1), payments(1), ledger(4), certificates(1), payouts(4), secondary_trades, ownership_events(1). GET /api/admin/ownership/{ownership_id}/trace also works. Verified via curl."
  - task: "A3 Block3/4 canonical ownership event kinds + certificate ownership events"
    implemented: true
    working: "NA"
    file: "lumen_unit_registry.py, lumen_certificates.py, lumen_secondary.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Registry ownership_events now carry canonical 'kind' (created/increased/decreased/transferred/closed). Certificate events extended with ownership_created/ownership_closed (reconcile) and ownership_split/ownership_merge (secondary trade hook). Needs E2E via a secondary trade: confirm split (seller partial) / merge (buyer consolidation) / closed (seller exits) events appear AND A1+A2 invariants stay green."

frontend:
  - task: "A3 Investor Portfolio Timeline 2.0 (/investor/journey)"
    implemented: true
    working: "NA"
    file: "pages/investor/InvestorJourney.js, layouts/InvestorLayout.js, components/MobileNav.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/investor/journey (nav 'Шлях інвестицій'). Expandable cards per investment with canonical-state badge + progress + vertical 8-step timeline (done/current/pending nodes with icons + timestamps). Visually verified (Стоянка active, 7/8)."
  - task: "A3 Admin Ownership Explorer trace drawer (in Unit Registry cap table)"
    implemented: true
    working: "NA"
    file: "pages/admin/AdminUnitRegistry.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "In /admin/registry → open asset → cap table now has a 'Trace' button per holder → opens right drawer with canonical-path chips + sections: Інвестиції, Платежі, Леджер, Сертифікати, Виплати, Вторинні угоди, Події володіння. Visually verified for Acme Client (LMN-2026-000003)."

metadata:
  created_by: "main_agent"
  version: "6.0"
  test_sequence: 5
  run_ui: true

test_plan:
  current_focus:
    - "A3 Lifecycle Engine + canonical state + investor timeline"
    - "A3 Block1 Certificate Binding (ownership_id <-> certificate_id)"
    - "A3 Block6 Ownership Explorer trace API"
    - "A3 Block3/4 canonical ownership event kinds + certificate ownership events"
    - "A3 Investor Portfolio Timeline 2.0 (/investor/journey)"
    - "A3 Admin Ownership Explorer trace drawer (in Unit Registry cap table)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "LUMEN 2.0 Phase A3 (Ownership Lifecycle) implemented. Logins: admin admin@atlas.dev/admin123, investor client@atlas.dev/client123. PLEASE TEST: (1) BACKEND: GET /api/investor/lifecycle (3 investments, each with canonical_state + 8 steps; verify steps intent/kyc/contract/payment/certificate/active/first_payout/withdrawal have correct done/current/pending), /api/investor/lifecycle/{investment_id}; GET /api/admin/lifecycle/states (counts); GET /api/admin/ownership/trace?investor_id=<id>&asset_id=asset-stoyanka-land (full trace with ownership.certificate_number bound, lifecycle, investments/payments/ledger/certificates/payouts/secondary_trades/ownership_events). To get an investor_id use /api/investor/lifecycle items[].investor_id. (2) BINDING + EVENTS + A1/A2 SAFETY (critical): as investor client@atlas.dev do a secondary buy-now on /investor/marketplace, then verify: (a) GET /api/admin/registry/invariants A1 all_ok=true, (b) GET /api/admin/certificates/invariants/check A2 all_ok=true, (c) ownership rows still bound to active certs (trace shows ownership.certificate_number), (d) certificate events include ownership_split/ownership_merge/transferred for the traded asset (check /api/admin/certificates/{id} events). (3) FRONTEND: /investor/journey (expand a card → vertical 8-step timeline with done steps green + current step), /admin/registry → open an asset → click 'Trace' on a holder row → drawer shows canonical-path chips + Інвестиції/Платежі/Леджер/Сертифікати/Виплати/Вторинні угоди/Події володіння sections. Skip drag/drop/voice/camera. Nothing mocked — all derived from real domain entities."

## (Older A2) user_problem_statement: "LUMEN 2.0 / Phase A2 — Certificate Engine. Turn technical unit-ownership (A1 registry) into an investor-facing Investment Certificate. Registry REMAINS source of truth; certificates are a reconciled projection. Issue on ownership; burn & re-issue on secondary trade (units change → old replaced/voided, new active). Append-only certificate_events. Public verification page /certificates/verify/:code (no private data). Investor /investor/certificates (active+history, PDF download, verify link). Admin /admin/certificates (filter, void, reissue, audit). PDF (reportlab) + QR (qrcode). NOT in scope: NFT/blockchain/crypto/e-sign/notary/tax. Invariants: active cert units == registry units; single active per (investor,asset); every active ownership has active cert; verify code unique. A1 invariants must stay green."

backend:
  - task: "Certificate Engine — issue/reconcile/burn&reissue/void + events + invariants"
    implemented: true
    working: true
    file: "lumen_certificates.py, server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Startup reconcile issued 5 active certs (one per active ownership). GET /api/admin/certificates → 5 active, counts correct. GET /api/admin/certificates/invariants/check → all_ok=true (active_units_match_registry, single_active_per_owner, every_active_ownership_has_cert, verify_codes_unique). GET /api/investor/certificates (client@atlas.dev) → 3 active certs (LMN-2026-0001/0003/0004). Verified via curl."
  - task: "Public verification — /api/public/certificates/verify/{code} (no private data)"
    implemented: true
    working: true
    file: "lumen_certificates.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/public/certificates/verify/DAE7-E6EF-7196 returns sanitized view (cert number, asset, SPV, units, %, status, valid). Confirmed it does NOT expose investor_id or investor_name. Records 'verified' event."
  - task: "Certificate PDF + QR generation"
    implemented: true
    working: true
    file: "lumen_certificates.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/investor/certificates/{id}/pdf returns valid application/pdf (%PDF header, 15.5KB) with reportlab layout + embedded QR (qrcode) pointing to the public verify URL. Records 'downloaded' event."
  - task: "Secondary burn & re-issue hook — registry-then-certificates"
    implemented: true
    working: "NA"
    file: "lumen_secondary.py, lumen_certificates.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "_settle_trade calls registry hook (6b) then certificate hook (6c): reconcile_asset → seller cert replaced/voided, buyer cert issued/reissued + 'transferred' events. Needs E2E: secondary buy-now, then verify seller's old active cert becomes replaced/voided, buyer gets active cert with new units, A2 invariants stay all_ok, AND A1 registry invariants stay all_ok."

frontend:
  - task: "Investor Certificates page — active+history, PDF, verify link, event history"
    implemented: true
    working: "NA"
    file: "pages/investor/InvestorCertificates.js, layouts/InvestorLayout.js, components/MobileNav.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/investor/certificates (nav 'Сертифікати'). Cards: number, asset, SPV, units/%/value, status badge, PDF (opens /pdf), Перевірити (opens /certificates/verify/:code), Історія drawer (events). 3 active certs visible. Visually verified."
  - task: "Admin Certificates page — filters, search, void, reissue, audit, reconcile, PDF"
    implemented: true
    working: "NA"
    file: "pages/admin/AdminCertificates.js, layouts/AdminLayout.js, components/MobileNav.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/admin/certificates (nav 'Сертифікати'). Counts (active/replaced/voided/expired/draft) + invariants pill + Звірити (reconcile). Filter tabs + search. Table → row click opens detail drawer with audit + Перевипустити (reissue) / Анулювати (void) / PDF. 5 active certs visible. Visually verified."
  - task: "Public Certificate Verify page — /certificates/verify/:code"
    implemented: true
    working: "NA"
    file: "pages/CertificateVerifyPage.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Public route (no auth). Reads :code, calls /api/public/certificates/verify/{code}, shows valid/invalid card with asset/SPV/units/%/date/code + 'private data not disclosed' note. Manual code entry form. Visually verified (valid cert renders green)."

metadata:
  created_by: "main_agent"
  version: "5.0"
  test_sequence: 4
  run_ui: true

test_plan:
  current_focus:
    - "Certificate Engine — issue/reconcile/burn&reissue/void + events + invariants"
    - "Public verification — no private data"
    - "Certificate PDF + QR generation"
    - "Secondary burn & re-issue hook — registry-then-certificates"
    - "Investor Certificates page"
    - "Admin Certificates page"
    - "Public Certificate Verify page"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "LUMEN 2.0 Phase A2 (Certificate Engine) implemented. Logins: admin admin@atlas.dev/admin123, investor client@atlas.dev/client123. A real verify code to test public page: DAE7-E6EF-7196 (Стоянка). PLEASE TEST: (1) BACKEND: GET /api/admin/certificates (5 active, counts), /api/admin/certificates/invariants/check (all_ok must be true), /api/investor/certificates (3 active for client), /api/public/certificates/verify/{code} (MUST NOT contain investor_id/investor_name), /api/investor/certificates/{id}/pdf (valid %PDF). Admin void: POST /api/admin/certificates/{id}/void {reason}; reissue: POST /api/admin/certificates/{id}/reissue; reconcile: POST /api/admin/certificates/reconcile. (2) BURN & RE-ISSUE + A1 SAFETY: as investor client@atlas.dev, do a secondary buy-now on /investor/marketplace, then verify: seller's previous active cert became replaced/voided, buyer has an active cert matching new registry units, A2 invariants stay all_ok=true, AND A1 registry invariants (GET /api/admin/registry/invariants) stay all_ok=true. (3) FRONTEND: /investor/certificates (cards, PDF opens, Перевірити opens public page, Історія drawer), /admin/certificates (counts, filters, search, row→detail drawer, Перевипустити/Анулювати, PDF, Звірити), public /certificates/verify/DAE7-E6EF-7196 (valid card, no private data) + an invalid code shows 'не знайдено'. Skip drag/drop/voice/camera. No mocked data — certificates derive from the real registry."

## (Older) user_problem_statement: "LUMEN 2.0 / Phase A1 — Unit Registry & Ownership OS. Replace the legacy float 'units' model (1 unit == 1 UAH) with a deterministic INTEGER unit registry: every asset has fixed total_units (100000), Ownership.units becomes integer, derived authoritatively from active investments ± secondary share-transfers via largest-remainder method. New collections: lumen_asset_units, lumen_ownership_events (append-only), lumen_ownership_snapshots. Admin Unit Registry Dashboard + Ownership Explorer (cap table + event stream + snapshot/recompute + invariants). Investor 'Мої частки' units view. Migration runs on startup (idempotent). Hooked into secondary settlement so trades emit transfer_in/out events and keep units conserved."

backend:
  - task: "Unit Registry engine — integer units, asset_units, migration, invariants"
    implemented: true
    working: true
    file: "lumen_unit_registry.py, server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Startup migration migrated 6 assets, all_invariants_ok=True. GET /api/admin/registry/summary returns totals (total 600000, issued 17612, available 582388, listed 3721) + per-asset. GET /api/admin/registry/invariants all_ok=True. GET /api/admin/registry/asset/{id} returns cap table (Стоянка: Acme Client 6250 units 6.25% 200000 UAH) + recent_events (genesis issue +6250). Verified via curl. Largest-remainder guarantees Σ holder units == issued ≤ total."
  - task: "Investor units API — /api/investor/units + per-asset events"
    implemented: true
    working: true
    file: "lumen_unit_registry.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/investor/units for client@atlas.dev returns total_units 11410, total_value 499989 UAH, 3 holdings (Стоянка 6250/6.25%, Лавр 3077/3.08%, Подільський 2083/2.08%). Verified via curl. GET /api/investor/units/{asset_id}/events returns the investor's own ownership events."
  - task: "Secondary-market hook — trades update integer registry + emit transfer events"
    implemented: true
    working: "NA"
    file: "lumen_secondary.py, lumen_unit_registry.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "_settle_trade now calls lumen_unit_registry.on_trade_settled after ownership rows update: re-derives integer units for the asset, emits transfer_out (seller) + transfer_in (buyer) ownership_events. Needs E2E: run a secondary buy-now trade and verify units conserved (seller↓ buyer↑, Σ unchanged) + events recorded + invariants still OK + payouts (ownership_percent) unaffected."

frontend:
  - task: "Admin Unit Registry Dashboard + Ownership Explorer"
    implemented: true
    working: "NA"
    file: "pages/admin/AdminUnitRegistry.js, layouts/AdminLayout.js, components/MobileNav.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/admin/registry (nav 'Реєстр одиниць'). Dashboard shows totals (Усього/Випущено/На вторинному ринку/Доступно) + asset cards (issued/available/holders + subscription bar + unit price) + invariants pill. Click asset → Ownership Explorer: stat tiles, invariant badge, cap table (інвестор/одиниці/частка/виставлено/вартість), event stream, Знімок + Перерахувати buttons. Visually verified via screenshot."
  - task: "Investor Units view — 'Мої частки'"
    implemented: true
    working: "NA"
    file: "pages/investor/InvestorUnits.js, layouts/InvestorLayout.js, components/MobileNav.js, App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/investor/units (nav 'Мої частки'). Summary (Усього одиниць / Поточна вартість / Активів) + per-asset holdings (cover, units, %, value) + 'Історія' drawer showing ownership events. Visually verified via screenshot."

metadata:
  created_by: "main_agent"
  version: "4.0"
  test_sequence: 3
  run_ui: true

test_plan:
  current_focus:
    - "Unit Registry engine — integer units, asset_units, migration, invariants"
    - "Investor units API — /api/investor/units + per-asset events"
    - "Secondary-market hook — trades update integer registry + emit transfer events"
    - "Admin Unit Registry Dashboard + Ownership Explorer"
    - "Investor Units view — 'Мої частки'"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "LUMEN 2.0 Phase A1 (Unit Registry & Ownership OS) implemented. Logins: admin admin@atlas.dev/admin123, investor client@atlas.dev/client123. PLEASE TEST: (1) BACKEND: GET /api/admin/registry/summary (totals + assets), /api/admin/registry/invariants (all_ok must be true), /api/admin/registry/asset/asset-stoyanka-land (cap table + events), /api/investor/units (investor holdings), /api/investor/units/{asset}/events. (2) CONSERVATION/SECONDARY: as investor client@atlas.dev (has holdings + 75000 wallet), perform a secondary buy-now of a small demo listing, then re-check /api/admin/registry/invariants stays all_ok=true AND that an ownership_event transfer_in/out pair was created AND units conserved (seller issued + buyer issued unchanged at asset level). Also confirm payouts/ownership_percent still intact (registry must NOT break existing payout/secondary flows). (3) FRONTEND: /admin/registry dashboard renders totals + asset cards; click an asset opens Ownership Explorer with cap table + event stream; Знімок (snapshot) and Перерахувати (recompute) work. /investor/units shows 'Мої частки' with units/%/value and 'Історія' drawer. Skip drag/drop/voice/camera. No mocked data — everything derives from the real domain registry."

## (Older) user_problem_statement: "LR-2a Legal Package (6 docs: Public Offer, Privacy, AML, KYC, Risk Disclosure, Secondary Market Terms) with dedicated /legal/* pages + UI integration (footer, registration, KYC, secondary market). LR-3a Operations SOP (5 internal compliance SOPs, admin-editable). LR-3b Admin Operations Center (/admin/operations aggregator over pending KYC/payments/withdrawals/payouts/disputes)."


backend:
  - task: "Legal package API (6 docs) — public package list + slug-aware document + admin editor with auto_seeded protection"
    implemented: true
    working: true
    file: "legal_settings.py, legal_content.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/public/legal-package returns 6 ordered items (offer/privacy/aml/kyc/risk/secondary). GET /api/public/legal-document/{slug} resolves slugs incl. secondary-market. Real UA content seeded via ensure_legal_package on startup (package v2). Admin PUT flags auto_seeded=false. Verified via curl."
  - task: "Operations SOP API — 5 SOPs, list/detail/edit/reset, idempotent seed"
    implemented: true
    working: true
    file: "ops_sop.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "GET /api/admin/sop (5 items), GET /api/admin/sop/{key}, PUT {key} (edit, sets auto_seeded=false), POST {key}/reset. Verified list via curl."
  - task: "Operations Center aggregator — /api/admin/operations/summary"
    implemented: true
    working: true
    file: "ops_center.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: true
          agent: "main"
          comment: "Aggregates pending KYC (lumen_investor_profiles), payments (lumen_payment_requests), withdrawals (lumen_withdrawal_requests), payouts (lumen_payout_batches), disputes (manual=0). 5 cards + total_pending. Verified via curl (payouts=1)."

frontend:
  - task: "Public Legal pages — /legal index + /legal/:slug document with TOC + MarkdownLite"
    implemented: true
    working: "NA"
    file: "pages/legal/LegalIndexPage.js, pages/legal/LegalDocPage.js, components/MarkdownLite.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Routes /legal and /legal/:slug. Index lists 6 cards; doc page renders markdown with sticky TOC cross-links + print. Visually verified via screenshot."
  - task: "Legal UI integration — footer links, registration consent checkbox, KYC policy links, secondary-market terms link"
    implemented: true
    working: "NA"
    file: "pages/LandingPage.js, pages/UnifiedAuthPage.js, pages/investor/InvestorProfile.js, pages/investor/InvestorMarketplace.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Footer 'Правова інформація' column + bottom-bar links → /legal/*. Register requires consent checkbox (data-testid auth-consent-checkbox) before submit. KYC card links to /legal/kyc, /legal/aml, /legal/privacy. Marketplace header links to /legal/secondary-market."
  - task: "Admin Operations Center + SOP pages with nav"
    implemented: true
    working: "NA"
    file: "pages/admin/AdminOperations.js, pages/admin/AdminSOP.js, layouts/AdminLayout.js, components/MobileNav.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "/admin/operations (nav 'Центр операцій') shows 5 cards + total. /admin/sop (nav 'Регламенти (SOP)') shows 5 SOPs + rendered doc + edit/save/reset. Visually verified via screenshot."

metadata:
  created_by: "main_agent"
  version: "3.0"
  test_sequence: 2
  run_ui: true

test_plan:
  current_focus:
    - "Legal package API (6 docs)"
    - "Operations SOP API"
    - "Operations Center aggregator"
    - "Public Legal pages"
    - "Legal UI integration"
    - "Admin Operations Center + SOP pages with nav"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "New LR-2a/LR-3a/LR-3b features implemented. Logins: admin admin@atlas.dev/admin123 (or demo-admin chip), investor client@atlas.dev/client123 (or demo-investor chip). Please test: (1) Backend APIs listed above. (2) Public /legal index → 6 cards → click opens /legal/offer; TOC cross-links navigate between docs; secondary-market slug resolves. (3) Landing footer legal links navigate to /legal/*. (4) Registration mode: submit disabled until consent checkbox checked, then registration works. (5) Investor profile KYC card has policy links. (6) Investor marketplace header has secondary-market terms link. (7) Admin /admin/operations renders 5 cards with counts + deep links; nav item 'Центр операцій'. (8) Admin /admin/sop renders 5 SOPs, opening one shows formatted document; Edit→change→Save persists; nav item 'Регламенти (SOP)'. Skip drag/drop/voice/camera. No mocked data."

## (Previous) user_problem_statement: "Sprint 13 — Secondary Market: Ownership → Listing → Bid/Buy → Trade → Settlement → Ledger. Finish to 100%. Core invariant: total ownership units per asset never change, only the owner. Test UI (InvestorMarketplace + AdminSecondaryMarket)."

backend:
  - task: "Secondary Market lifecycle + invariant + ledger/fee/wallet conservation"
    implemented: true
    working: true
    file: "lumen_secondary.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "E2E test (tests/test_sprint13_secondary_e2e.py) 63/63 PASS. Full lifecycle buy-now + offer/accept, invariant total ownership unchanged across trades, ledger Σ=0, wallet conservation, platform fee 1%, all guards. FIXED bug: ownership upsert was missing id on insert -> DuplicateKeyError for brand-new buyers (added $setOnInsert id). Consistency check I1-I13 all green after demo seed."

frontend:
  - task: "InvestorMarketplace — browse listings, holdings/sell, buy-now, make offer, my-listings/bids/trades, cancel"
    implemented: true
    working: "NA"
    file: "pages/investor/InvestorMarketplace.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Page routed at /investor/marketplace, sidebar nav 'Вторинний ринок' added. 2 demo listings visible. Needs UI E2E: tabs (Огляд/Мої частки/Мої лістинги/Мої офери/Угоди), create listing from holdings, buy-now, make offer."
  - task: "AdminSecondaryMarket — overview KPIs + trades/listings monitoring"
    implemented: true
    working: "NA"
    file: "pages/admin/AdminSecondaryMarket.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Routed /admin/secondary-market, sidebar nav added. Calls /admin/secondary/overview. Needs UI check of KPIs and recent trades."

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: true

test_plan:
  current_focus:
    - "InvestorMarketplace — browse listings, holdings/sell, buy-now, make offer"
    - "AdminSecondaryMarket — overview KPIs + trades monitoring"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "Sprint 13 backend fully verified by E2E (63/63). Please test FRONTEND UI for secondary market. Logins: investor client@atlas.dev/client123 (has 75000 wallet + holdings to sell); admin admin@atlas.dev/admin123. Demo listings exist (ЖК Подільський 90000@0.97, ТЦ Лавр 120000@1.03 from 'Інвестор #5fc84f'). Test investor: open /investor/marketplace, all 5 tabs, create a listing from 'Мої частки' (sell part of a holding), buy-now a demo listing (~48500), make an offer below price. Test admin: /admin/secondary-market overview KPIs + trades. Skip any drag/drop/voice/camera."
