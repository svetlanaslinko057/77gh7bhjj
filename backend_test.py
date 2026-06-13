"""
LUMEN 2.0 Phase A3 — Ownership Lifecycle Backend Testing
Tests all lifecycle APIs, certificate binding, ownership trace, and A1/A2 invariants.
"""
import requests
import sys
import json
from datetime import datetime

BASE_URL = "https://code-setup-10.preview.emergentagent.com/api"

class A3LifecycleTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_session = None
        self.investor_session = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def log(self, msg, level="INFO"):
        """Log test messages"""
        prefix = "✅" if level == "PASS" else "❌" if level == "FAIL" else "🔍"
        print(f"{prefix} {msg}")

    def test(self, name, condition, details=""):
        """Run a test assertion"""
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            self.log(f"PASS: {name}", "PASS")
            if details:
                print(f"   └─ {details}")
        else:
            self.tests_failed += 1
            self.failures.append(f"{name}: {details}")
            self.log(f"FAIL: {name} - {details}", "FAIL")

    def login(self, email, password, role="investor"):
        """Login and get session token"""
        self.log(f"Logging in as {email}...")
        try:
            resp = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("session_token") or data.get("token")
                if token:
                    self.log(f"Login successful for {email}", "PASS")
                    return token
                else:
                    self.log(f"Login response missing token: {data}", "FAIL")
                    return None
            else:
                self.log(f"Login failed: {resp.status_code} - {resp.text}", "FAIL")
                return None
        except Exception as e:
            self.log(f"Login error: {str(e)}", "FAIL")
            return None

    def get(self, endpoint, session=None, params=None):
        """GET request with optional auth session"""
        try:
            if session:
                resp = session.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=15
                )
            else:
                resp = requests.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=15
                )
            return resp
        except Exception as e:
            self.log(f"GET {endpoint} error: {str(e)}", "FAIL")
            return None

    def post(self, endpoint, session=None, json_data=None):
        """POST request with optional auth session"""
        try:
            if session:
                resp = session.post(
                    f"{self.base_url}{endpoint}",
                    json=json_data,
                    timeout=15
                )
            else:
                resp = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=json_data,
                    timeout=15
                )
            return resp
        except Exception as e:
            self.log(f"POST {endpoint} error: {str(e)}", "FAIL")
            return None

    # ========================================================================
    # TEST SUITE
    # ========================================================================

    def test_auth(self):
        """Test authentication for both admin and investor"""
        self.log("\n=== TEST: Authentication ===")
        
        self.admin_session = self.login("admin@atlas.dev", "admin123", "admin")
        self.test("Admin login", self.admin_session is not None)
        
        self.investor_session = self.login("client@atlas.dev", "client123", "investor")
        self.test("Investor login", self.investor_session is not None)

    def test_investor_lifecycle(self):
        """Test GET /api/investor/lifecycle"""
        self.log("\n=== TEST: Investor Lifecycle (Portfolio Timeline 2.0) ===")
        
        resp = self.get("/investor/lifecycle", self.investor_session)
        self.test("GET /investor/lifecycle returns 200", resp and resp.status_code == 200)
        
        if not resp or resp.status_code != 200:
            return
        
        data = resp.json()
        items = data.get("items", [])
        
        self.test("Returns items array", isinstance(items, list))
        self.test("Has at least 1 investment", len(items) >= 1, f"Found {len(items)} investments")
        
        if len(items) == 0:
            return
        
        # Check first investment structure
        inv = items[0]
        self.test("Investment has investment_id", "investment_id" in inv)
        self.test("Investment has canonical_state", "canonical_state" in inv)
        self.test("Investment has certificate_number", "certificate_number" in inv or inv.get("certificate_number") is None)
        self.test("Investment has units", "units" in inv)
        self.test("Investment has steps array", "steps" in inv and isinstance(inv.get("steps"), list))
        
        # Check 8-step timeline
        steps = inv.get("steps", [])
        self.test("Has 8 steps in timeline", len(steps) == 8, f"Found {len(steps)} steps")
        
        if len(steps) == 8:
            expected_keys = ["intent", "kyc", "contract", "payment", "certificate", "active", "first_payout", "withdrawal"]
            actual_keys = [s.get("key") for s in steps]
            self.test("Steps have correct keys", actual_keys == expected_keys, f"Keys: {actual_keys}")
            
            # Check step structure
            for step in steps:
                if not all(k in step for k in ["key", "label", "status"]):
                    self.test(f"Step {step.get('key')} has required fields", False, f"Missing fields in {step}")
                    break
            else:
                self.test("All steps have required fields (key, label, status)", True)
            
            # Check status values
            statuses = [s.get("status") for s in steps]
            valid_statuses = all(s in ["done", "current", "pending"] for s in statuses)
            self.test("All steps have valid status", valid_statuses, f"Statuses: {statuses}")
        
        # Check progress
        progress = inv.get("progress", 0)
        total_steps = inv.get("total_steps", 0)
        self.test("Has progress tracking", progress >= 0 and total_steps == 8, 
                  f"Progress: {progress}/{total_steps}")
        
        # Log sample investment for inspection
        self.log(f"\nSample investment:")
        self.log(f"  ID: {inv.get('investment_id')}")
        self.log(f"  Asset: {inv.get('asset_title')}")
        self.log(f"  State: {inv.get('canonical_state')} ({inv.get('canonical_state_label')})")
        self.log(f"  Certificate: {inv.get('certificate_number') or 'None'}")
        self.log(f"  Units: {inv.get('units')}")
        self.log(f"  Progress: {progress}/{total_steps} steps")

    def test_investor_lifecycle_detail(self):
        """Test GET /api/investor/lifecycle/{investment_id}"""
        self.log("\n=== TEST: Investor Lifecycle Detail ===")
        
        # First get an investment_id
        resp = self.get("/investor/lifecycle", self.investor_token)
        if not resp or resp.status_code != 200:
            self.test("Cannot test detail - lifecycle list failed", False)
            return
        
        items = resp.json().get("items", [])
        if len(items) == 0:
            self.test("Cannot test detail - no investments", False)
            return
        
        investment_id = items[0].get("investment_id")
        self.log(f"Testing detail for investment: {investment_id}")
        
        resp = self.get(f"/investor/lifecycle/{investment_id}", self.investor_session)
        self.test("GET /investor/lifecycle/{id} returns 200", resp and resp.status_code == 200)
        
        if resp and resp.status_code == 200:
            data = resp.json()
            self.test("Detail has investment_id", data.get("investment_id") == investment_id)
            self.test("Detail has canonical_state", "canonical_state" in data)
            self.test("Detail has steps", "steps" in data and len(data.get("steps", [])) == 8)

    def test_admin_lifecycle_states(self):
        """Test GET /api/admin/lifecycle/states"""
        self.log("\n=== TEST: Admin Lifecycle States ===")
        
        resp = self.get("/admin/lifecycle/states", self.admin_session)
        self.test("GET /admin/lifecycle/states returns 200", resp and resp.status_code == 200)
        
        if not resp or resp.status_code != 200:
            return
        
        data = resp.json()
        self.test("Has states array", "states" in data)
        self.test("Has labels dict", "labels" in data)
        self.test("Has counts dict", "counts" in data)
        
        counts = data.get("counts", {})
        active_count = counts.get("active", 0)
        self.test("Active state count >= 3", active_count >= 3, f"Active count: {active_count}")
        
        self.log(f"\nLifecycle state counts:")
        for state, count in counts.items():
            if count > 0:
                label = data.get("labels", {}).get(state, state)
                self.log(f"  {state} ({label}): {count}")

    def test_ownership_trace(self):
        """Test GET /api/admin/ownership/trace"""
        self.log("\n=== TEST: Ownership Explorer - Full Trace ===")
        
        # First get an investor_id from lifecycle
        resp = self.get("/investor/lifecycle", self.investor_session)
        if not resp or resp.status_code != 200:
            self.test("Cannot test trace - lifecycle failed", False)
            return
        
        items = resp.json().get("items", [])
        if len(items) == 0:
            self.test("Cannot test trace - no investments", False)
            return
        
        investor_id = items[0].get("investor_id")
        asset_id = "asset-stoyanka-land"
        
        self.log(f"Testing trace for investor: {investor_id}, asset: {asset_id}")
        
        resp = self.get("/admin/ownership/trace", self.admin_session, 
                       params={"investor_id": investor_id, "asset_id": asset_id})
        self.test("GET /admin/ownership/trace returns 200", resp and resp.status_code == 200)
        
        if not resp or resp.status_code != 200:
            return
        
        trace = resp.json()
        
        # Check trace structure
        self.test("Trace has investor_id", trace.get("investor_id") == investor_id)
        self.test("Trace has asset_id", trace.get("asset_id") == asset_id)
        self.test("Trace has ownership", "ownership" in trace)
        self.test("Trace has lifecycle", "lifecycle" in trace)
        self.test("Trace has investments", "investments" in trace)
        self.test("Trace has payments", "payments" in trace)
        self.test("Trace has ledger", "ledger" in trace)
        self.test("Trace has certificates", "certificates" in trace)
        self.test("Trace has payouts", "payouts" in trace)
        self.test("Trace has secondary_trades", "secondary_trades" in trace)
        self.test("Trace has ownership_events", "ownership_events" in trace)
        
        # Check certificate binding (Block1)
        ownership = trace.get("ownership")
        if ownership:
            cert_num = ownership.get("certificate_number")
            cert_id = ownership.get("certificate_id")
            self.test("Ownership has certificate_number bound", cert_num is not None, 
                     f"Certificate: {cert_num}")
            self.test("Ownership has certificate_id bound", cert_id is not None)
            
            self.log(f"\nOwnership binding:")
            self.log(f"  Ownership ID: {ownership.get('id')}")
            self.log(f"  Certificate ID: {cert_id}")
            self.log(f"  Certificate Number: {cert_num}")
            self.log(f"  Units: {ownership.get('units_int')}")
        
        # Log trace summary
        self.log(f"\nTrace summary:")
        self.log(f"  Investments: {len(trace.get('investments', []))}")
        self.log(f"  Payments: {len(trace.get('payments', []))}")
        self.log(f"  Ledger entries: {len(trace.get('ledger', []))}")
        self.log(f"  Certificates: {len(trace.get('certificates', []))}")
        self.log(f"  Payouts: {len(trace.get('payouts', []))}")
        self.log(f"  Secondary trades: {len(trace.get('secondary_trades', []))}")
        self.log(f"  Ownership events: {len(trace.get('ownership_events', []))}")

    def test_ownership_trace_by_id(self):
        """Test GET /api/admin/ownership/{ownership_id}/trace"""
        self.log("\n=== TEST: Ownership Trace by ID ===")
        
        # First get an ownership_id from trace
        resp = self.get("/investor/lifecycle", self.investor_session)
        if not resp or resp.status_code != 200:
            self.test("Cannot test trace by id - lifecycle failed", False)
            return
        
        items = resp.json().get("items", [])
        if len(items) == 0:
            self.test("Cannot test trace by id - no investments", False)
            return
        
        ownership_id = items[0].get("ownership_id")
        if not ownership_id:
            self.test("Cannot test trace by id - no ownership_id in lifecycle", False)
            return
        
        self.log(f"Testing trace for ownership_id: {ownership_id}")
        
        resp = self.get(f"/admin/ownership/{ownership_id}/trace", self.admin_session)
        self.test("GET /admin/ownership/{id}/trace returns 200", resp and resp.status_code == 200)
        
        if resp and resp.status_code == 200:
            trace = resp.json()
            self.test("Trace by ID has ownership", "ownership" in trace)
            self.test("Trace by ID has lifecycle", "lifecycle" in trace)

    def test_a1_invariants(self):
        """Test A1 Unit Registry invariants"""
        self.log("\n=== TEST: A1 Unit Registry Invariants ===")
        
        resp = self.get("/admin/registry/invariants", self.admin_session)
        self.test("GET /admin/registry/invariants returns 200", resp and resp.status_code == 200)
        
        if not resp or resp.status_code != 200:
            return
        
        data = resp.json()
        all_ok = data.get("all_ok", False)
        self.test("A1 invariants all_ok = true", all_ok == True, 
                 f"all_ok: {all_ok}")
        
        assets = data.get("assets", [])
        self.log(f"\nA1 Invariant check for {len(assets)} assets:")
        for asset in assets:
            ok = asset.get("ok", False)
            checks = asset.get("checks", {})
            self.log(f"  {asset.get('asset_title')}: {'✅ OK' if ok else '❌ FAIL'}")
            if not ok:
                for check, result in checks.items():
                    if not result:
                        self.log(f"    ❌ {check}: {result}")

    def test_a2_invariants(self):
        """Test A2 Certificate Engine invariants"""
        self.log("\n=== TEST: A2 Certificate Engine Invariants ===")
        
        resp = self.get("/admin/certificates/invariants/check", self.admin_session)
        self.test("GET /admin/certificates/invariants/check returns 200", 
                 resp and resp.status_code == 200)
        
        if not resp or resp.status_code != 200:
            return
        
        data = resp.json()
        all_ok = data.get("all_ok", False)
        self.test("A2 invariants all_ok = true", all_ok == True, 
                 f"all_ok: {all_ok}")
        
        checks = data.get("checks", {})
        self.log(f"\nA2 Invariant checks:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            self.log(f"  {status} {check}: {result}")
        
        violations = data.get("violations", [])
        if violations:
            self.log(f"\n⚠️  Found {len(violations)} violations:")
            for v in violations[:5]:  # Show first 5
                self.log(f"  {v}")

    def test_certificate_binding(self):
        """Test Block1: Certificate Binding (ownership_id <-> certificate_id)"""
        self.log("\n=== TEST: Block1 Certificate Binding ===")
        
        # Get trace to check binding
        resp = self.get("/investor/lifecycle", self.investor_session)
        if not resp or resp.status_code != 200:
            self.test("Cannot test binding - lifecycle failed", False)
            return
        
        items = resp.json().get("items", [])
        if len(items) == 0:
            self.test("Cannot test binding - no investments", False)
            return
        
        investor_id = items[0].get("investor_id")
        asset_id = items[0].get("asset_id")
        
        resp = self.get("/admin/ownership/trace", self.admin_session,
                       params={"investor_id": investor_id, "asset_id": asset_id})
        
        if not resp or resp.status_code != 200:
            self.test("Cannot test binding - trace failed", False)
            return
        
        trace = resp.json()
        ownership = trace.get("ownership")
        
        if not ownership:
            self.test("Cannot test binding - no ownership in trace", False)
            return
        
        # Check bidirectional binding
        cert_id = ownership.get("certificate_id")
        cert_num = ownership.get("certificate_number")
        
        self.test("Ownership has certificate_id", cert_id is not None)
        self.test("Ownership has certificate_number", cert_num is not None)
        
        # Verify certificate points back to ownership
        if cert_id:
            resp = self.get(f"/admin/certificates/{cert_id}", self.admin_session)
            if resp and resp.status_code == 200:
                cert_data = resp.json()
                cert = cert_data.get("certificate", {})
                ownership_id_in_cert = cert.get("ownership_id")
                self.test("Certificate has ownership_id pointing back", 
                         ownership_id_in_cert == ownership.get("id"),
                         f"Cert ownership_id: {ownership_id_in_cert}, Ownership id: {ownership.get('id')}")

    def run_all_tests(self):
        """Run all test suites"""
        self.log("=" * 70)
        self.log("LUMEN 2.0 Phase A3 — Ownership Lifecycle Backend Tests")
        self.log("=" * 70)
        
        # Run tests in order
        self.test_auth()
        
        if not self.admin_session or not self.investor_session:
            self.log("\n❌ Authentication failed - cannot continue tests", "FAIL")
            return False
        
        self.test_investor_lifecycle()
        self.test_investor_lifecycle_detail()
        self.test_admin_lifecycle_states()
        self.test_ownership_trace()
        self.test_ownership_trace_by_id()
        self.test_certificate_binding()
        self.test_a1_invariants()
        self.test_a2_invariants()
        
        # Summary
        self.log("\n" + "=" * 70)
        self.log(f"TEST SUMMARY")
        self.log("=" * 70)
        self.log(f"Total tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed} ✅")
        self.log(f"Failed: {self.tests_failed} ❌")
        
        if self.tests_failed > 0:
            self.log("\n❌ FAILURES:")
            for failure in self.failures:
                self.log(f"  • {failure}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"\nSuccess rate: {success_rate:.1f}%")
        
        return self.tests_failed == 0


def main():
    tester = A3LifecycleTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
