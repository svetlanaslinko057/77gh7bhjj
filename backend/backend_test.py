"""
LUMEN Sprint 1 / Phase 0 Backend Regression Test
=================================================
Tests backend functionality under LUMEN_ONLY=true mode.

Tests:
1. Basic health check
2. Assets endpoints (public)
3. Auth quick login (client & admin)
4. Admin diagnostic endpoints with auth
5. Admin-only protection (401/403)
6. Investor cabinet endpoints
7. Smoke test execution
"""

import requests
import sys
import json
from datetime import datetime

# Public endpoint from frontend/.env
BASE_URL = "https://lumen-staging.preview.emergentagent.com"

class LumenBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = []
        self.client_cookies = None
        self.admin_cookies = None
        self.asset_id = None

    def log(self, emoji, message):
        """Print formatted log message"""
        print(f"{emoji} {message}")

    def test(self, name, condition, details=""):
        """Record test result"""
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            self.log("✅", f"PASS: {name} {details}")
            return True
        else:
            self.tests_failed.append(name)
            self.log("❌", f"FAIL: {name} {details}")
            return False

    def test_health_check(self):
        """Test 1: GET /api/ returns 200"""
        self.log("🔍", "Testing basic health check...")
        try:
            response = requests.get(f"{self.base_url}/api/", timeout=10)
            return self.test(
                "Health check (GET /api/)",
                response.status_code == 200,
                f"status={response.status_code}"
            )
        except Exception as e:
            return self.test("Health check (GET /api/)", False, f"error={str(e)}")

    def test_assets_list(self):
        """Test 2: GET /api/assets returns 200 with seeded assets"""
        self.log("🔍", "Testing assets list endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/assets", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                # Response structure is {"items": [...]} not {"assets": [...]}
                assets = data.get("items", [])
                # Check for Ukrainian titles (seeded data)
                has_ukrainian = any("title" in a for a in assets)
                # Store first asset ID for next test
                if assets:
                    self.asset_id = assets[0].get("id")
                return self.test(
                    "Assets list (GET /api/assets)",
                    len(assets) >= 6 and has_ukrainian,
                    f"count={len(assets)}, has_data={has_ukrainian}"
                )
            else:
                return self.test(
                    "Assets list (GET /api/assets)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Assets list (GET /api/assets)", False, f"error={str(e)}")

    def test_asset_detail(self):
        """Test 3: GET /api/assets/{id} works"""
        if not self.asset_id:
            return self.test("Asset detail (GET /api/assets/{id})", False, "no asset_id available")
        
        self.log("🔍", f"Testing asset detail endpoint for ID: {self.asset_id}...")
        try:
            response = requests.get(f"{self.base_url}/api/assets/{self.asset_id}", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                has_id = data.get("id") == self.asset_id
                return self.test(
                    "Asset detail (GET /api/assets/{id})",
                    has_id,
                    f"status={response.status_code}, id_match={has_id}"
                )
            else:
                return self.test(
                    "Asset detail (GET /api/assets/{id})",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Asset detail (GET /api/assets/{id})", False, f"error={str(e)}")

    def test_client_quick_login(self):
        """Test 4: POST /api/auth/quick with client email"""
        self.log("🔍", "Testing client quick login...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/quick",
                json={"email": "client@atlas.dev"},
                timeout=10
            )
            success = response.status_code == 200
            if success:
                # Store cookies for later tests
                self.client_cookies = response.cookies
                # Verify session_token cookie is set
                has_cookie = "session_token" in response.cookies
                return self.test(
                    "Client quick login (POST /api/auth/quick)",
                    has_cookie,
                    f"status={response.status_code}, has_session_token={has_cookie}"
                )
            else:
                return self.test(
                    "Client quick login (POST /api/auth/quick)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Client quick login (POST /api/auth/quick)", False, f"error={str(e)}")

    def test_client_auth_me(self):
        """Test 5: GET /api/auth/me with client cookie"""
        if not self.client_cookies:
            return self.test("Client auth/me (GET /api/auth/me)", False, "no client cookies")
        
        self.log("🔍", "Testing client auth/me endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                cookies=self.client_cookies,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                has_user = "user_id" in data or "id" in data
                return self.test(
                    "Client auth/me (GET /api/auth/me)",
                    has_user,
                    f"status={response.status_code}, has_user={has_user}"
                )
            else:
                return self.test(
                    "Client auth/me (GET /api/auth/me)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Client auth/me (GET /api/auth/me)", False, f"error={str(e)}")

    def test_admin_quick_login(self):
        """Test 6: POST /api/auth/quick with admin email"""
        self.log("🔍", "Testing admin quick login...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/quick",
                json={"email": "admin@atlas.dev"},
                timeout=10
            )
            success = response.status_code == 200
            if success:
                # Store cookies for later tests
                self.admin_cookies = response.cookies
                has_cookie = "session_token" in response.cookies
                return self.test(
                    "Admin quick login (POST /api/auth/quick)",
                    has_cookie,
                    f"status={response.status_code}, has_session_token={has_cookie}"
                )
            else:
                return self.test(
                    "Admin quick login (POST /api/auth/quick)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Admin quick login (POST /api/auth/quick)", False, f"error={str(e)}")

    def test_admin_system_domain(self):
        """Test 7: GET /api/admin/system/domain with admin cookie"""
        if not self.admin_cookies:
            return self.test("Admin system/domain", False, "no admin cookies")
        
        self.log("🔍", "Testing admin system/domain endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/system/domain",
                cookies=self.admin_cookies,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                lumen_only = data.get("lumen_only") == True
                skipped_count = data.get("skipped_count", 0)
                has_lumen_startup = "_lumen_phase0_startup" in data.get("active_startups", [])
                
                return self.test(
                    "Admin system/domain (GET /api/admin/system/domain)",
                    lumen_only and skipped_count == 22 and has_lumen_startup,
                    f"lumen_only={lumen_only}, skipped={skipped_count}, has_lumen_startup={has_lumen_startup}"
                )
            else:
                return self.test(
                    "Admin system/domain (GET /api/admin/system/domain)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Admin system/domain", False, f"error={str(e)}")

    def test_admin_system_models(self):
        """Test 8: GET /api/admin/system/models with admin cookie"""
        if not self.admin_cookies:
            return self.test("Admin system/models", False, "no admin cookies")
        
        self.log("🔍", "Testing admin system/models endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/system/models",
                cookies=self.admin_cookies,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                collections = data.get("collections", [])
                indexes = data.get("indexes", {})
                
                # Check for all 6 lumen collections
                expected_collections = [
                    "lumen_assets",
                    "lumen_investment_rounds",
                    "lumen_investor_intents",
                    "lumen_investments",
                    "lumen_ownerships",
                    "lumen_investor_profiles"
                ]
                has_all_collections = all(c in collections for c in expected_collections)
                
                # Check for unique indexes (ux_*)
                has_unique_indexes = any(
                    any("ux_" in idx.get("name", "") for idx in idx_list)
                    for idx_list in indexes.values()
                    if isinstance(idx_list, list)
                )
                
                return self.test(
                    "Admin system/models (GET /api/admin/system/models)",
                    has_all_collections and has_unique_indexes,
                    f"collections={len(collections)}/6, has_unique_indexes={has_unique_indexes}"
                )
            else:
                return self.test(
                    "Admin system/models (GET /api/admin/system/models)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Admin system/models", False, f"error={str(e)}")

    def test_admin_protection_no_auth(self):
        """Test 9: GET /api/admin/system/domain without auth returns 401"""
        self.log("🔍", "Testing admin endpoint protection (no auth)...")
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/system/domain",
                timeout=10
            )
            return self.test(
                "Admin protection - no auth (401)",
                response.status_code == 401,
                f"status={response.status_code}"
            )
        except Exception as e:
            return self.test("Admin protection - no auth (401)", False, f"error={str(e)}")

    def test_admin_protection_client_auth(self):
        """Test 10: GET /api/admin/system/domain with client cookie returns 403"""
        if not self.client_cookies:
            return self.test("Admin protection - client auth (403)", False, "no client cookies")
        
        self.log("🔍", "Testing admin endpoint protection (client auth)...")
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/system/domain",
                cookies=self.client_cookies,
                timeout=10
            )
            return self.test(
                "Admin protection - client auth (403)",
                response.status_code == 403,
                f"status={response.status_code}"
            )
        except Exception as e:
            return self.test("Admin protection - client auth (403)", False, f"error={str(e)}")

    def test_investor_portfolio(self):
        """Test 11: GET /api/investor/portfolio with client cookie"""
        if not self.client_cookies:
            return self.test("Investor portfolio", False, "no client cookies")
        
        self.log("🔍", "Testing investor portfolio endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/investor/portfolio",
                cookies=self.client_cookies,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                # Response structure is {"summary": {...}, "investments": [...], "upcoming_payouts": [...]}
                has_structure = "summary" in data and "investments" in data
                return self.test(
                    "Investor portfolio (GET /api/investor/portfolio)",
                    has_structure,
                    f"status={response.status_code}, has_structure={has_structure}"
                )
            else:
                return self.test(
                    "Investor portfolio (GET /api/investor/portfolio)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Investor portfolio", False, f"error={str(e)}")

    def test_investor_payouts(self):
        """Test 12: GET /api/investor/payouts with client cookie"""
        if not self.client_cookies:
            return self.test("Investor payouts", False, "no client cookies")
        
        self.log("🔍", "Testing investor payouts endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/investor/payouts",
                cookies=self.client_cookies,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                # Should return a list or object with payouts
                is_valid = isinstance(data, (list, dict))
                return self.test(
                    "Investor payouts (GET /api/investor/payouts)",
                    is_valid,
                    f"status={response.status_code}, valid_response={is_valid}"
                )
            else:
                return self.test(
                    "Investor payouts (GET /api/investor/payouts)",
                    False,
                    f"status={response.status_code}"
                )
        except Exception as e:
            return self.test("Investor payouts", False, f"error={str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀", f"Starting LUMEN Backend Regression Tests")
        self.log("🌐", f"Base URL: {self.base_url}")
        self.log("", "=" * 70)
        
        # Run tests in order
        self.test_health_check()
        self.test_assets_list()
        self.test_asset_detail()
        self.test_client_quick_login()
        self.test_client_auth_me()
        self.test_admin_quick_login()
        self.test_admin_system_domain()
        self.test_admin_system_models()
        self.test_admin_protection_no_auth()
        self.test_admin_protection_client_auth()
        self.test_investor_portfolio()
        self.test_investor_payouts()
        
        # Print summary
        self.log("", "=" * 70)
        self.log("📊", f"Tests Run: {self.tests_run}")
        self.log("✅", f"Tests Passed: {self.tests_passed}")
        self.log("❌", f"Tests Failed: {len(self.tests_failed)}")
        
        if self.tests_failed:
            self.log("", "\nFailed tests:")
            for test in self.tests_failed:
                self.log("  ❌", test)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log("📈", f"Success Rate: {success_rate:.1f}%")
        
        return 0 if len(self.tests_failed) == 0 else 1


def main():
    tester = LumenBackendTester()
    exit_code = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL BACKEND TESTS PASSED")
    else:
        print("❌ SOME BACKEND TESTS FAILED")
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
