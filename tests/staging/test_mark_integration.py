"""
Staging integration tests using Playwright.
Tests DB write (create duck location) and read (verify via page and API).

Requires environment variables:
  STG_BASE_URL - staging URL (e.g., https://stg.duckiehunt.com)
  STG_TEST_USERNAME - Django superuser username
  STG_TEST_PASSWORD - Django superuser password

Run with: pytest tests/staging/test_mark_integration.py -v
"""
import os
import uuid

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def base_url():
    url = os.environ.get("STG_BASE_URL", "http://localhost:8042")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def test_username():
    username = os.environ.get("STG_TEST_USERNAME")
    if not username:
        pytest.skip("STG_TEST_USERNAME not set")
    return username


@pytest.fixture(scope="session")
def test_password():
    password = os.environ.get("STG_TEST_PASSWORD")
    if not password:
        pytest.skip("STG_TEST_PASSWORD not set")
    return password


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context for all tests."""
    return {"ignore_https_errors": True}


@pytest.fixture()
def authenticated_page(page: Page, base_url, test_username, test_password):
    """Log in via Django admin and return an authenticated page."""
    page.goto(f"{base_url}/admin/login/")
    # Wait for the login form to be fully rendered
    page.locator("#id_username").wait_for(state="visible", timeout=10000)
    page.locator("#id_username").click()
    page.locator("#id_username").fill(test_username)
    page.locator("#id_password").click()
    page.locator("#id_password").fill(test_password)
    page.locator('input[type="submit"]').click()
    # Wait for navigation away from login page
    page.wait_for_load_state("networkidle")
    # If login failed, we'll still be on the login page with an error
    if "/admin/login" in page.url:
        error = page.locator(".errornote").text_content() or "Unknown login error"
        raise AssertionError(f"Admin login failed: {error}")
    return page


# Use a high duck_id to avoid collisions with real data
TEST_DUCK_ID = "2998"


class TestMarkDuckIntegration:
    """End-to-end test: create a duck location and verify it exists."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.unique_comment = f"playwright-test-{uuid.uuid4().hex[:8]}"

    def test_create_and_verify_duck_location(
        self, authenticated_page: Page, base_url
    ):
        """
        1. Navigate to /mark/
        2. Fill in the form (no captcha needed for authenticated user)
        3. Submit and verify redirect to location page
        4. Verify the location page shows correct data
        5. Verify the API returns the new location
        """
        page = authenticated_page

        # Step 1: Navigate to mark page
        page.goto(f"{base_url}/mark/{TEST_DUCK_ID}")
        expect(page.locator("form")).to_be_visible()

        # Verify no captcha widget is shown for authenticated user
        assert page.locator(".g-recaptcha").count() == 0

        # Step 2: Fill the form
        # Duck ID should be pre-filled from URL
        duck_id_input = page.locator("input[name='duck_id']")
        expect(duck_id_input).to_have_value(TEST_DUCK_ID)

        # Fill location (the Places autocomplete might not work in test,
        # so fill lat/lng directly via JS since they are hidden inputs)
        page.fill("input[name='location']", "Test Location, Staging")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '29.9511'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-90.0715'")
        # Fill date_time (required datetime-local field)
        page.fill("input[name='date_time']", "2026-01-15T12:00")
        page.fill("textarea[name='comments']", self.unique_comment)

        # Step 3: Submit
        page.click("text=Submit new location")

        # Should redirect to the new location page
        page.wait_for_url("**/location/**", timeout=10000)
        location_url = page.url
        assert "/location/" in location_url

        # Step 4: Verify the location page content
        page_content = page.content()
        assert self.unique_comment in page_content or TEST_DUCK_ID in page_content

        # Step 5: Verify via API
        page.goto(f"{base_url}/api/duck/{TEST_DUCK_ID}/locations")
        api_text = page.locator("body").inner_text()
        assert self.unique_comment in api_text

    def test_duck_detail_page_after_creation(
        self, authenticated_page: Page, base_url
    ):
        """Verify the duck detail page renders with location data."""
        page = authenticated_page
        page.goto(f"{base_url}/duck/{TEST_DUCK_ID}")

        expect(page.locator("body")).to_contain_text(TEST_DUCK_ID)
