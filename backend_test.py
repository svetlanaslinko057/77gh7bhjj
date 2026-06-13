#!/usr/bin/env python3
"""
Phase C Community OS Backend Testing
Tests all community endpoints: public, auth gating, holder flow, non-holder gating, admin
"""
import requests
import sys
from datetime import datetime

BASE_URL = "https://arch-review-25.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@atlas.dev"
ADMIN_PASSWORD = "admin123"
CLIENT_EMAIL = "client@atlas.dev"
CLIENT_PASSWORD = "client123"

# Test assets
ASSET_HOLDER = "asset-podilskyi"  # client@atlas.dev owns units here
ASSET_NON_HOLDER = "asset-rivne-warehouse"  # client@atlas.dev does NOT own units here
ASSET_ADMIN_TEST = "asset-lavr-tc"  # for admin tests

class CommunityTester:
    def __init__(self):
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def log(self, msg, level="INFO"):
        print(f"[{level}] {msg}")

    def test(self, name, fn):
        """Run a single test"""
        self.tests_run += 1
        self.log(f"\n{'='*60}")
        self.log(f"TEST {self.tests_run}: {name}")
        self.log('='*60)
        try:
            fn()
            self.tests_passed += 1
            self.log(f"✅ PASSED: {name}", "PASS")
        except AssertionError as e:
            self.tests_failed += 1
            self.failures.append(f"{name}: {str(e)}")
            self.log(f"❌ FAILED: {name} - {str(e)}", "FAIL")
        except Exception as e:
            self.tests_failed += 1
            self.failures.append(f"{name}: {str(e)}")
            self.log(f"❌ ERROR: {name} - {str(e)}", "ERROR")

    def login(self, email, password):
        """Login and store cookies"""
        self.log(f"Logging in as {email}...")
        r = self.session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
        self.log(f"✓ Logged in as {email}")
        return r.json()

    def logout(self):
        """Clear session"""
        self.session.cookies.clear()
        self.log("✓ Logged out")

    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC (NO AUTH) TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    def test_public_summary(self):
        """Public GET /api/assets/{asset}/community/summary"""
        self.logout()
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/summary")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        # Check required fields
        assert data.get("holders_count", 0) > 0, "holders_count should be > 0"
        assert "sentiment" in data, "sentiment missing"
        sentiment = data["sentiment"]
        assert "positive" in sentiment, "sentiment.positive missing"
        assert "neutral" in sentiment, "sentiment.neutral missing"
        assert "negative" in sentiment, "sentiment.negative missing"
        assert "label" in sentiment, "sentiment.label missing"
        assert data.get("posts_count", 0) >= 0, "posts_count missing"
        assert "open_polls" in data, "open_polls missing"
        self.log(f"✓ Summary: holders={data['holders_count']}, sentiment={sentiment['label']}, posts={data['posts_count']}, polls={data['open_polls']}")

    def test_public_feed(self):
        """Public GET /api/assets/{asset}/community/feed - should only see public posts"""
        self.logout()
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/feed")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert "items" in data, "items missing"
        assert data.get("can_see_lounge") == False, "Anon should NOT see lounge"
        
        # Check that only public posts are visible (announcements + questions)
        items = data["items"]
        for post in items:
            assert post["kind"] in ["announcement", "question"], f"Anon should only see announcements/questions, got {post['kind']}"
            assert post.get("visibility") == "public", f"Anon should only see public posts, got {post.get('visibility')}"
        
        self.log(f"✓ Feed: {len(items)} public posts, can_see_lounge={data['can_see_lounge']}")

    def test_public_polls(self):
        """Public GET /api/assets/{asset}/community/polls"""
        self.logout()
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/polls")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert "items" in data, "items missing"
        items = data["items"]
        
        # Check poll structure
        for poll in items:
            assert "options" in poll, "poll.options missing"
            for opt in poll["options"]:
                assert "units" in opt, "option.units missing"
                assert "percent" in opt, "option.percent missing"
        
        self.log(f"✓ Polls: {len(items)} polls with weighted options")

    def test_public_leaderboard(self):
        """Public GET /api/assets/{asset}/community/leaderboard"""
        self.logout()
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/leaderboard")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert "items" in data, "items missing"
        items = data["items"]
        
        # Check leaderboard structure
        for row in items:
            assert "tier_label" in row, "tier_label missing"
            assert "score" in row, "score missing"
        
        self.log(f"✓ Leaderboard: {len(items)} rows with tier_label")

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTH GATING TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    def test_anon_post_blocked(self):
        """Anon POST /api/assets/{asset}/community/posts should return 401/403"""
        self.logout()
        r = self.session.post(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/posts", 
                             json={"kind": "question", "title": "Test", "body": "Testing anon post"})
        assert r.status_code in [401, 403], f"Expected 401/403, got {r.status_code}"
        self.log(f"✓ Anon post blocked with {r.status_code}")

    def test_anon_vote_blocked(self):
        """Anon POST /api/community/polls/{poll_id}/vote should return 401"""
        self.logout()
        # First get a poll ID
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/polls")
        if r.status_code == 200 and r.json().get("items"):
            poll_id = r.json()["items"][0]["id"]
            r = self.session.post(f"{BASE_URL}/community/polls/{poll_id}/vote", 
                                 json={"option_key": "opt1"})
            assert r.status_code == 401, f"Expected 401, got {r.status_code}"
            self.log(f"✓ Anon vote blocked with {r.status_code}")
        else:
            self.log("⚠ No polls available to test anon vote blocking")

    # ═══════════════════════════════════════════════════════════════════════════
    # HOLDER FLOW TESTS (client@atlas.dev on asset-podilskyi)
    # ═══════════════════════════════════════════════════════════════════════════

    def test_holder_summary(self):
        """Holder GET /api/assets/{asset}/community/summary should show is_holder=true"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/summary")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("is_holder") == True, "is_holder should be True"
        assert data.get("units", 0) > 0, "units should be > 0"
        self.log(f"✓ Holder summary: is_holder={data['is_holder']}, units={data['units']}")

    def test_holder_feed_lounge(self):
        """Holder GET /api/assets/{asset}/community/feed should include discussion posts"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/feed")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("can_see_lounge") == True, "Holder should see lounge"
        
        # Check for discussion posts
        items = data["items"]
        has_discussion = any(p["kind"] == "discussion" for p in items)
        self.log(f"✓ Holder feed: {len(items)} posts, can_see_lounge={data['can_see_lounge']}, has_discussion={has_discussion}")

    def test_holder_post_discussion(self):
        """Holder POST /api/assets/{asset}/community/posts with kind='discussion'"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.post(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/posts",
                             json={"kind": "discussion", "title": "QA lounge", "body": "testing holder access"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("visibility") == "holders", "Discussion should be holders-only"
        self.log(f"✓ Holder posted discussion: id={data['id']}, visibility={data['visibility']}")
        return data["id"]

    def test_holder_post_question(self):
        """Holder POST /api/assets/{asset}/community/posts with kind='question'"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.post(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/posts",
                             json={"kind": "question", "title": "QA q", "body": "a question for operator"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("visibility") == "public", "Question should be public"
        self.log(f"✓ Holder posted question: id={data['id']}, visibility={data['visibility']}")
        return data["id"]

    def test_holder_comment(self):
        """Holder POST /api/community/posts/{post_id}/comments"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        
        # First get a post to comment on
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/feed")
        if r.status_code == 200 and r.json().get("items"):
            post_id = r.json()["items"][0]["id"]
            r = self.session.post(f"{BASE_URL}/community/posts/{post_id}/comments",
                                 json={"body": "nice"})
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            self.log(f"✓ Holder commented on post {post_id}")
        else:
            self.log("⚠ No posts available to test commenting")

    def test_holder_react(self):
        """Holder POST /api/community/posts/{post_id}/react"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        
        # First get a post to react to
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/feed")
        if r.status_code == 200 and r.json().get("items"):
            post_id = r.json()["items"][0]["id"]
            r = self.session.post(f"{BASE_URL}/community/posts/{post_id}/react",
                                 json={"reaction": "like"})
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert "active" in data, "active field missing"
            self.log(f"✓ Holder reacted to post {post_id}, active={data['active']}")
        else:
            self.log("⚠ No posts available to test reacting")

    def test_holder_sentiment(self):
        """Holder POST /api/assets/{asset}/community/sentiment"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.post(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/sentiment",
                             json={"mood": "positive"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("my_sentiment") == "positive", "my_sentiment should be 'positive'"
        assert "sentiment" in data, "aggregated sentiment missing"
        self.log(f"✓ Holder set sentiment: my_sentiment={data['my_sentiment']}")

    def test_holder_vote(self):
        """Holder POST /api/community/polls/{poll_id}/vote"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        
        # First get an open poll
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_HOLDER}/community/polls")
        if r.status_code == 200:
            polls = [p for p in r.json().get("items", []) if p.get("status") == "open"]
            if polls:
                poll = polls[0]
                poll_id = poll["id"]
                option_key = poll["options"][0]["key"]
                
                r = self.session.post(f"{BASE_URL}/community/polls/{poll_id}/vote",
                                     json={"option_key": option_key})
                assert r.status_code == 200, f"Expected 200, got {r.status_code}"
                data = r.json()
                
                assert data.get("poll", {}).get("my_vote") == option_key, "my_vote should match"
                assert data.get("poll", {}).get("total_units", 0) > 0, "total_units should increase"
                self.log(f"✓ Holder voted: poll={poll_id}, option={option_key}, total_units={data['poll']['total_units']}")
            else:
                self.log("⚠ No open polls available to test voting")
        else:
            self.log("⚠ Could not fetch polls to test voting")

    # ═══════════════════════════════════════════════════════════════════════════
    # NON-HOLDER GATING TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    def test_non_holder_discussion_blocked(self):
        """Non-holder POST discussion on asset they don't own should return 403"""
        self.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        r = self.session.post(f"{BASE_URL}/assets/{ASSET_NON_HOLDER}/community/posts",
                             json={"kind": "discussion", "title": "Test", "body": "Should fail"})
        assert r.status_code == 403, f"Expected 403, got {r.status_code}"
        self.log(f"✓ Non-holder discussion blocked with {r.status_code}")

    # ═══════════════════════════════════════════════════════════════════════════
    # ADMIN TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    def test_admin_announcement(self):
        """Admin POST /api/admin/assets/{asset}/community/announcements"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        r = self.session.post(f"{BASE_URL}/admin/assets/{ASSET_ADMIN_TEST}/community/announcements",
                             json={"title": "QA announce", "body": "x"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("ok") == True, "ok should be True"
        assert "notified" in data, "notified count missing"
        self.log(f"✓ Admin announcement: notified={data['notified']} holders")

    def test_admin_poll(self):
        """Admin POST /api/admin/assets/{asset}/community/polls"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        r = self.session.post(f"{BASE_URL}/admin/assets/{ASSET_ADMIN_TEST}/community/polls",
                             json={"question": "QA poll?", "options": ["A", "B"], "closes_in_days": 7})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        
        assert data.get("ok") == True, "ok should be True"
        assert "poll" in data, "poll missing"
        assert data["poll"].get("id"), "poll.id missing"
        self.log(f"✓ Admin poll created: id={data['poll']['id']}")
        return data["poll"]["id"]

    def test_admin_close_poll(self):
        """Admin POST /api/admin/community/polls/{poll_id}/close"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # First create a poll
        r = self.session.post(f"{BASE_URL}/admin/assets/{ASSET_ADMIN_TEST}/community/polls",
                             json={"question": "Test close", "options": ["A", "B"], "closes_in_days": 7})
        if r.status_code == 200:
            poll_id = r.json()["poll"]["id"]
            r = self.session.post(f"{BASE_URL}/admin/community/polls/{poll_id}/close")
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert data.get("ok") == True, "ok should be True"
            self.log(f"✓ Admin closed poll: id={poll_id}")
        else:
            self.log("⚠ Could not create poll to test closing")

    def test_admin_answer_question(self):
        """Admin POST /api/admin/community/posts/{post_id}/answer"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # First get a question post
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_ADMIN_TEST}/community/feed?filter=questions")
        if r.status_code == 200:
            questions = [p for p in r.json().get("items", []) if p.get("kind") == "question" and not p.get("answer")]
            if questions:
                post_id = questions[0]["id"]
                r = self.session.post(f"{BASE_URL}/admin/community/posts/{post_id}/answer",
                                     json={"answer": "operator reply"})
                assert r.status_code == 200, f"Expected 200, got {r.status_code}"
                data = r.json()
                assert data.get("ok") == True, "ok should be True"
                assert data.get("post", {}).get("answer") == "operator reply", "answer not set"
                self.log(f"✓ Admin answered question: post={post_id}")
            else:
                self.log("⚠ No unanswered questions to test answering")
        else:
            self.log("⚠ Could not fetch questions to test answering")

    def test_admin_pin_post(self):
        """Admin POST /api/admin/community/posts/{post_id}/pin"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # First get a post
        r = self.session.get(f"{BASE_URL}/assets/{ASSET_ADMIN_TEST}/community/feed")
        if r.status_code == 200 and r.json().get("items"):
            post_id = r.json()["items"][0]["id"]
            r = self.session.post(f"{BASE_URL}/admin/community/posts/{post_id}/pin")
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert data.get("ok") == True, "ok should be True"
            assert "pinned" in data, "pinned field missing"
            self.log(f"✓ Admin toggled pin: post={post_id}, pinned={data['pinned']}")
        else:
            self.log("⚠ No posts available to test pinning")

    def test_admin_delete_post(self):
        """Admin DELETE /api/admin/community/posts/{post_id}"""
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # First create a test post as admin (via announcement)
        r = self.session.post(f"{BASE_URL}/admin/assets/{ASSET_ADMIN_TEST}/community/announcements",
                             json={"title": "Test delete", "body": "Will be deleted"})
        if r.status_code == 200:
            post_id = r.json()["post"]["id"]
            r = self.session.delete(f"{BASE_URL}/admin/community/posts/{post_id}")
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
            data = r.json()
            assert data.get("ok") == True, "ok should be True"
            self.log(f"✓ Admin deleted post: id={post_id}")
        else:
            self.log("⚠ Could not create post to test deletion")

    # ═══════════════════════════════════════════════════════════════════════════
    # RUN ALL TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    def run_all(self):
        """Run all tests"""
        self.log("\n" + "="*60)
        self.log("PHASE C COMMUNITY OS - BACKEND TESTING")
        self.log("="*60)
        
        # PUBLIC TESTS
        self.log("\n" + "─"*60)
        self.log("PUBLIC (NO AUTH) TESTS")
        self.log("─"*60)
        self.test("Public summary", self.test_public_summary)
        self.test("Public feed (anon sees only public posts)", self.test_public_feed)
        self.test("Public polls", self.test_public_polls)
        self.test("Public leaderboard", self.test_public_leaderboard)
        
        # AUTH GATING TESTS
        self.log("\n" + "─"*60)
        self.log("AUTH GATING TESTS")
        self.log("─"*60)
        self.test("Anon post blocked", self.test_anon_post_blocked)
        self.test("Anon vote blocked", self.test_anon_vote_blocked)
        
        # HOLDER FLOW TESTS
        self.log("\n" + "─"*60)
        self.log("HOLDER FLOW TESTS (client@atlas.dev on asset-podilskyi)")
        self.log("─"*60)
        self.test("Holder summary", self.test_holder_summary)
        self.test("Holder feed includes lounge", self.test_holder_feed_lounge)
        self.test("Holder post discussion", self.test_holder_post_discussion)
        self.test("Holder post question", self.test_holder_post_question)
        self.test("Holder comment", self.test_holder_comment)
        self.test("Holder react", self.test_holder_react)
        self.test("Holder set sentiment", self.test_holder_sentiment)
        self.test("Holder vote", self.test_holder_vote)
        
        # NON-HOLDER GATING TESTS
        self.log("\n" + "─"*60)
        self.log("NON-HOLDER GATING TESTS")
        self.log("─"*60)
        self.test("Non-holder discussion blocked", self.test_non_holder_discussion_blocked)
        
        # ADMIN TESTS
        self.log("\n" + "─"*60)
        self.log("ADMIN TESTS")
        self.log("─"*60)
        self.test("Admin announcement", self.test_admin_announcement)
        self.test("Admin create poll", self.test_admin_poll)
        self.test("Admin close poll", self.test_admin_close_poll)
        self.test("Admin answer question", self.test_admin_answer_question)
        self.test("Admin pin post", self.test_admin_pin_post)
        self.test("Admin delete post", self.test_admin_delete_post)
        
        # SUMMARY
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        self.log(f"Total tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed}")
        self.log(f"Failed: {self.tests_failed}")
        
        if self.failures:
            self.log("\n" + "─"*60)
            self.log("FAILURES:")
            self.log("─"*60)
            for failure in self.failures:
                self.log(f"  • {failure}", "FAIL")
        
        return 0 if self.tests_failed == 0 else 1


if __name__ == "__main__":
    tester = CommunityTester()
    sys.exit(tester.run_all())
