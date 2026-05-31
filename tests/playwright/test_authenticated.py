"""
Playwright tests that require authentication (auth.json).

These tests verify behavior specific to logged-in users, such as:
- Submitting without captcha when logged in (even with real keys)
- Profile-linked sightings
- User-specific UI elements

Requires:
  - Local dev server running at http://localhost:8042
  - Valid auth.json (run: npx playwright codegen http://localhost:8042 --save-storage=auth.json)

Run with:
  pytest tests/playwright/test_authenticated.py -v
  pytest tests/playwright/test_authenticated.py -v --headed
"""
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")
AUTH_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "auth.json")
FIXTURE_IMAGE = os.path.join(os.path.dirname(__file__), "fixtures", "test_duck.jpg")


def _auth_available():
    """Check if auth.json exists and is non-empty."""
    return os.path.exists(AUTH_FILE) and os.path.getsize(AUTH_FILE) > 10


@pytest.fixture(scope="session")
def browser_context_args():
    if not _auth_available():
        pytest.skip("auth.json not found — run: npx playwright codegen http://localhost:8042 --save-storage=auth.json")
    return {
        "storage_state": AUTH_FILE,
        "ignore_https_errors": True,
    }


@pytest.fixture()
def authenticated_page(page: Page):
    """Navigate to homepage and verify we're logged in."""
    page.goto(BASE_URL)
    # Logged-in users see "Logout" in navbar, not "Login"
    if page.locator("a.nav-link:has-text('Login')").count() > 0:
        pytest.skip("Not logged in — auth.json may be stale. Regenerate with: npx playwright codegen http://localhost:8042 --save-storage=auth.json")
    return page


class TestAuthenticatedMark:
    """Tests for the mark form when logged in."""

    def test_no_captcha_shown(self, authenticated_page: Page):
        """Logged-in users should not see captcha."""
        page = authenticated_page
        assert page.locator(".g-recaptcha").count() == 0

    def test_submit_sighting_with_image(self, authenticated_page: Page):
        """Full submit with image upload as authenticated user."""
        page = authenticated_page
        test_duck_id = "8888"

        page.goto(f"{BASE_URL}/mark/{test_duck_id}")
        expect(page.locator("form")).to_be_visible()

        page.fill("input[name='duck_id']", test_duck_id)
        page.fill("input[name='location']", "Auth Test Location")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.2672'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.7431'")
        page.fill("input[name='date_time']", "2026-01-15T12:00")
        page.fill("textarea[name='comments']", "Authenticated upload test")

        page.locator("input[name='image']").set_input_files(FIXTURE_IMAGE)
        page.click("text=Submit new location")

        page.wait_for_url("**/location/**", timeout=15000)
        assert "/location/" in page.url

        # Verify the location page has correct data
        body = page.locator("body")
        expect(body).to_contain_text(test_duck_id)
        expect(body).to_contain_text("Auth Test Location")
        expect(body).to_contain_text("Authenticated upload test")
        expect(body).to_contain_text("30.26")
        expect(body).to_contain_text("-97.74")

        # Verify photo thumbnail is displayed (requires FLICKR_API_KEY)
        photos_section = page.locator("text=Photos")
        if photos_section.count() > 0:
            photo_img = page.locator("img.img-fluid")
            expect(photo_img.first).to_be_visible()

    def test_username_in_navbar(self, authenticated_page: Page):
        """Logged-in users should see their username in the navbar."""
        page = authenticated_page
        page.goto(BASE_URL)
        # Should show username link instead of "Login"
        assert page.locator("a.nav-link", has_text="Login").count() == 0
        assert page.locator("a.nav-link", has_text="Logout").count() == 1


class TestAuthenticatedProfile:
    """Tests for user profile page."""

    def test_profile_page_loads(self, authenticated_page: Page):
        """Profile page should be accessible when logged in."""
        page = authenticated_page
        page.goto(f"{BASE_URL}/profile")
        expect(page.locator("body")).to_contain_text("Profile")
