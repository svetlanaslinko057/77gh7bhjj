#!/bin/bash

# LUMEN 2.0 Phase A3 — Ownership Lifecycle Backend Testing
# Tests all lifecycle APIs, certificate binding, ownership trace, and A1/A2 invariants

BASE_URL="https://code-setup-10.preview.emergentagent.com/api"
COOKIE_FILE="/tmp/test_cookies.txt"
ADMIN_COOKIE="/tmp/admin_cookies.txt"
INVESTOR_COOKIE="/tmp/investor_cookies.txt"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}🔍 $1${NC}"
}

pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
}

fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    if [ -n "$2" ]; then
        echo -e "${RED}   └─ $2${NC}"
    fi
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
}

test_condition() {
    local name="$1"
    local condition="$2"
    local details="$3"
    
    if [ "$condition" = "true" ]; then
        pass "$name"
        if [ -n "$details" ]; then
            echo "   └─ $details"
        fi
    else
        fail "$name" "$details"
    fi
}

# Login functions
login_admin() {
    log "Logging in as admin@atlas.dev..."
    response=$(curl -s -c "$ADMIN_COOKIE" -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@atlas.dev","password":"admin123"}')
    
    if echo "$response" | grep -q "user_id"; then
        pass "Admin login successful"
        return 0
    else
        fail "Admin login failed" "$response"
        return 1
    fi
}

login_investor() {
    log "Logging in as client@atlas.dev..."
    response=$(curl -s -c "$INVESTOR_COOKIE" -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"client@atlas.dev","password":"client123"}')
    
    if echo "$response" | grep -q "user_id"; then
        pass "Investor login successful"
        return 0
    else
        fail "Investor login failed" "$response"
        return 1
    fi
}

# Test functions
test_investor_lifecycle() {
    log "\n=== TEST: Investor Lifecycle (Portfolio Timeline 2.0) ==="
    
    response=$(curl -s -b "$INVESTOR_COOKIE" "$BASE_URL/investor/lifecycle")
    
    # Check if response contains items
    if echo "$response" | grep -q '"items"'; then
        pass "GET /investor/lifecycle returns data"
        
        # Count investments
        count=$(echo "$response" | grep -o '"investment_id"' | wc -l)
        test_condition "Has at least 1 investment" "$([ $count -ge 1 ] && echo true || echo false)" "Found $count investments"
        
        # Check for required fields
        echo "$response" | grep -q '"canonical_state"' && pass "Has canonical_state field" || fail "Missing canonical_state"
        echo "$response" | grep -q '"steps"' && pass "Has steps array" || fail "Missing steps array"
        echo "$response" | grep -q '"certificate_number"' && pass "Has certificate_number field" || fail "Missing certificate_number"
        
        # Save first investment_id for detail test
        INVESTMENT_ID=$(echo "$response" | grep -o '"investment_id":"[^"]*"' | head -1 | cut -d'"' -f4)
        INVESTOR_ID=$(echo "$response" | grep -o '"investor_id":"[^"]*"' | head -1 | cut -d'"' -f4)
        
        log "Sample investment ID: $INVESTMENT_ID"
        log "Investor ID: $INVESTOR_ID"
    else
        fail "GET /investor/lifecycle failed" "$response"
    fi
}

test_investor_lifecycle_detail() {
    log "\n=== TEST: Investor Lifecycle Detail ==="
    
    if [ -z "$INVESTMENT_ID" ]; then
        fail "Cannot test detail - no investment_id available"
        return
    fi
    
    response=$(curl -s -b "$INVESTOR_COOKIE" "$BASE_URL/investor/lifecycle/$INVESTMENT_ID")
    
    if echo "$response" | grep -q '"investment_id"'; then
        pass "GET /investor/lifecycle/{id} returns data"
        echo "$response" | grep -q '"canonical_state"' && pass "Detail has canonical_state" || fail "Detail missing canonical_state"
        echo "$response" | grep -q '"steps"' && pass "Detail has steps" || fail "Detail missing steps"
    else
        fail "GET /investor/lifecycle/{id} failed" "$response"
    fi
}

test_admin_lifecycle_states() {
    log "\n=== TEST: Admin Lifecycle States ==="
    
    response=$(curl -s -b "$ADMIN_COOKIE" "$BASE_URL/admin/lifecycle/states")
    
    if echo "$response" | grep -q '"states"'; then
        pass "GET /admin/lifecycle/states returns data"
        echo "$response" | grep -q '"counts"' && pass "Has counts" || fail "Missing counts"
        
        # Check active count
        active_count=$(echo "$response" | grep -o '"active":[0-9]*' | grep -o '[0-9]*')
        test_condition "Active state count >= 3" "$([ $active_count -ge 3 ] && echo true || echo false)" "Active count: $active_count"
        
        log "Lifecycle state counts:"
        echo "$response" | grep -o '"[a-z_]*":[0-9]*' | while read line; do
            log "  $line"
        done
    else
        fail "GET /admin/lifecycle/states failed" "$response"
    fi
}

test_ownership_trace() {
    log "\n=== TEST: Ownership Explorer - Full Trace ==="
    
    if [ -z "$INVESTOR_ID" ]; then
        fail "Cannot test trace - no investor_id available"
        return
    fi
    
    ASSET_ID="asset-stoyanka-land"
    log "Testing trace for investor: $INVESTOR_ID, asset: $ASSET_ID"
    
    response=$(curl -s -b "$ADMIN_COOKIE" "$BASE_URL/admin/ownership/trace?investor_id=$INVESTOR_ID&asset_id=$ASSET_ID")
    
    if echo "$response" | grep -q '"investor_id"'; then
        pass "GET /admin/ownership/trace returns data"
        
        # Check trace structure
        echo "$response" | grep -q '"ownership"' && pass "Trace has ownership" || fail "Missing ownership"
        echo "$response" | grep -q '"lifecycle"' && pass "Trace has lifecycle" || fail "Missing lifecycle"
        echo "$response" | grep -q '"investments"' && pass "Trace has investments" || fail "Missing investments"
        echo "$response" | grep -q '"payments"' && pass "Trace has payments" || fail "Missing payments"
        echo "$response" | grep -q '"ledger"' && pass "Trace has ledger" || fail "Missing ledger"
        echo "$response" | grep -q '"certificates"' && pass "Trace has certificates" || fail "Missing certificates"
        echo "$response" | grep -q '"payouts"' && pass "Trace has payouts" || fail "Missing payouts"
        echo "$response" | grep -q '"secondary_trades"' && pass "Trace has secondary_trades" || fail "Missing secondary_trades"
        echo "$response" | grep -q '"ownership_events"' && pass "Trace has ownership_events" || fail "Missing ownership_events"
        
        # Check certificate binding
        if echo "$response" | grep -q '"certificate_number":"LMN-'; then
            pass "Ownership has certificate_number bound"
            cert_num=$(echo "$response" | grep -o '"certificate_number":"[^"]*"' | head -1 | cut -d'"' -f4)
            log "Certificate number: $cert_num"
        else
            fail "Ownership missing certificate_number binding"
        fi
        
        # Save ownership_id for next test
        OWNERSHIP_ID=$(echo "$response" | grep -o '"id":"own-[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -z "$OWNERSHIP_ID" ]; then
            # Try alternative pattern
            OWNERSHIP_ID=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('ownership', {}).get('id', ''))" 2>/dev/null)
        fi
    else
        fail "GET /admin/ownership/trace failed" "$response"
    fi
}

test_ownership_trace_by_id() {
    log "\n=== TEST: Ownership Trace by ID ==="
    
    if [ -z "$OWNERSHIP_ID" ]; then
        fail "Cannot test trace by id - no ownership_id available"
        return
    fi
    
    log "Testing trace for ownership_id: $OWNERSHIP_ID"
    
    response=$(curl -s -b "$ADMIN_COOKIE" "$BASE_URL/admin/ownership/$OWNERSHIP_ID/trace")
    
    if echo "$response" | grep -q '"ownership"'; then
        pass "GET /admin/ownership/{id}/trace returns data"
        echo "$response" | grep -q '"lifecycle"' && pass "Trace by ID has lifecycle" || fail "Missing lifecycle"
    else
        fail "GET /admin/ownership/{id}/trace failed" "$response"
    fi
}

test_a1_invariants() {
    log "\n=== TEST: A1 Unit Registry Invariants ==="
    
    response=$(curl -s -b "$ADMIN_COOKIE" "$BASE_URL/admin/registry/invariants")
    
    if echo "$response" | grep -q '"all_ok"'; then
        all_ok=$(echo "$response" | grep -o '"all_ok":[a-z]*' | cut -d':' -f2)
        test_condition "A1 invariants all_ok = true" "$([ "$all_ok" = "true" ] && echo true || echo false)" "all_ok: $all_ok"
        
        log "A1 Invariant check:"
        echo "$response" | grep -o '"asset_title":"[^"]*"' | while read line; do
            log "  $line"
        done
    else
        fail "GET /admin/registry/invariants failed" "$response"
    fi
}

test_a2_invariants() {
    log "\n=== TEST: A2 Certificate Engine Invariants ==="
    
    response=$(curl -s -b "$ADMIN_COOKIE" "$BASE_URL/admin/certificates/invariants/check")
    
    if echo "$response" | grep -q '"all_ok"'; then
        all_ok=$(echo "$response" | grep -o '"all_ok":[a-z]*' | cut -d':' -f2)
        test_condition "A2 invariants all_ok = true" "$([ "$all_ok" = "true" ] && echo true || echo false)" "all_ok: $all_ok"
        
        log "A2 Invariant checks:"
        echo "$response" | grep -o '"[a-z_]*":[a-z]*' | while read line; do
            log "  $line"
        done
    else
        fail "GET /admin/certificates/invariants/check failed" "$response"
    fi
}

# Main test execution
main() {
    echo "======================================================================"
    log "LUMEN 2.0 Phase A3 — Ownership Lifecycle Backend Tests"
    echo "======================================================================"
    
    # Authentication
    log "\n=== TEST: Authentication ==="
    login_admin || exit 1
    login_investor || exit 1
    
    # Run all tests
    test_investor_lifecycle
    test_investor_lifecycle_detail
    test_admin_lifecycle_states
    test_ownership_trace
    test_ownership_trace_by_id
    test_a1_invariants
    test_a2_invariants
    
    # Summary
    echo ""
    echo "======================================================================"
    log "TEST SUMMARY"
    echo "======================================================================"
    log "Total tests: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED ✅${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED ❌${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        success_rate=100
    else
        success_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
    fi
    log "Success rate: ${success_rate}%"
    
    # Cleanup
    rm -f "$ADMIN_COOKIE" "$INVESTOR_COOKIE"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

main
