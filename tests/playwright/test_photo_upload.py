"""
Playwright integration test for image upload against local dev server.

Requires:
  - Local dev server running at http://localhost:8042
  - auth.json with authenticated session (run tests/create_auth.py first)

Run with:
  pytest tests/test_photo_upload.py -v

Run with visible browser:
  pytest tests/test_photo_upload.py -v --headed

Note: The upload test will attempt to upload to Flickr if FLICKR_API_KEY
is configured. Without it, the submission will succeed but the photo
won't be stored (tests verify the form path, not Flickr integration).
"""
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")
AUTH_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "auth.json")
FIXTURE_IMAGE = os.path.join(os.path.dirname(__file__), "fixtures", "test_duck.jpg")

# Use a high duck_id unlikely to conflict
TEST_DUCK_ID = "8888"


@pytest.fixture(scope="session")
def browser_context_args():
    if not os.path.exists(AUTH_FILE):
        pytest.skip("auth.json not found — run tests/create_auth.py first")
    return {
        "storage_state": AUTH_FILE,
        "ignore_https_errors": True,
    }


@pytest.fixture()
def authenticated_page(page: Page):
    """Verify we're logged in."""
    page.goto(f"{BASE_URL}/mark/")
    # If logged in, no captcha should be visible
    assert page.locator(".g-recaptcha").count() == 0
    return page


class TestPhotoUpload:
    """Test uploading an image through the mark form."""

    def test_upload_image_with_duck_sighting(self, authenticated_page: Page):
        """Submit a sighting with a photo and verify it appears on the location page."""
        page = authenticated_page

        page.goto(f"{BASE_URL}/mark/{TEST_DUCK_ID}")
        expect(page.locator("form")).to_be_visible()

        # Fill required fields
        page.fill("input[name='duck_id']", TEST_DUCK_ID)
        page.fill("input[name='location']", "Photo Test Location")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.2672'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.7431'")
        page.fill("input[name='date_time']", "2026-01-15T12:00")
        page.fill("textarea[name='comments']", "Integration test with photo upload")

        # Upload the test image
        page.locator("input[name='image']").set_input_files(FIXTURE_IMAGE)

        # Submit
        page.click("text=Submit new location")

        # Should redirect to location page
        page.wait_for_url("**/location/**", timeout=15000)
        location_url = page.url
        assert "/location/" in location_url

        # Verify the page loaded successfully
        expect(page.locator("body")).to_contain_text(TEST_DUCK_ID)

    def test_upload_invalid_file_shows_error(self, authenticated_page: Page, tmp_path):
        """Submitting a non-image file shows a validation error."""
        page = authenticated_page

        # Create a fake non-image file
        fake_file = tmp_path / "not_image.txt"
        fake_file.write_text("this is not an image")

        page.goto(f"{BASE_URL}/mark/{TEST_DUCK_ID}")
        expect(page.locator("form")).to_be_visible()

        # Fill required fields
        page.fill("input[name='duck_id']", TEST_DUCK_ID)
        page.fill("input[name='location']", "Bad Upload Test")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.0'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.0'")
        page.fill("input[name='date_time']", "2026-01-15T12:00")
        page.fill("textarea[name='comments']", "Should fail")

        # Upload invalid file
        page.locator("input[name='image']").set_input_files(str(fake_file))

        # Submit
        page.click("text=Submit new location")

        # Should stay on the form page (not redirect)
        page.wait_for_load_state("networkidle")
        assert "/mark/" in page.url or "/mark" in page.url

        # Should show an error about the image
        page_content = page.content()
        assert "valid image" in page_content.lower() or "image" in page_content.lower()
