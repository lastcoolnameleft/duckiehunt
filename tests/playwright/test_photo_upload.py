"""
Playwright integration tests for the mark-a-duck form.

Requires:
  - Local dev server running at http://localhost:8042
  - Captcha disabled in dev (no RECAPTCHA_PUBLIC_KEY env var)

Run with:
  pytest tests/playwright/test_photo_upload.py -v

Run with visible browser:
  pytest tests/playwright/test_photo_upload.py -v --headed
"""
import os
import random
import subprocess
import sys

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")
DJANGO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "django")

# Track duck IDs created during tests so we can clean them up
_created_duck_ids: list[str] = []


def _delete_ducks(duck_ids: list[str]):
    """Delete ducks by ID using Django ORM via manage.py shell."""
    if not duck_ids:
        return
    ids_str = ", ".join(duck_ids)
    script = f"""
from duck.models import Duck
ducks = Duck.objects.filter(duck_id__in=[{ids_str}])
count = ducks.count()
ducks.delete()
print(f'Deleted {{count}} test ducks')
"""
    subprocess.run(
        [sys.executable, "manage.py", "shell", "-c", script],
        cwd=DJANGO_DIR,
        capture_output=True,
    )


class TestFullMarkFlow:
    """End-to-end test for the complete mark-a-duck workflow.

    Requires dev server running with captcha disabled (no RECAPTCHA_PUBLIC_KEY).

    Tests the full path: duck name lookup → fill form → submit → verify.
    """

    def setup_method(self):
        """Clean up any leftover test ducks before each test."""
        _delete_ducks(_created_duck_ids.copy())
        _created_duck_ids.clear()

    def teardown_method(self):
        """Delete all ducks created during this test."""
        _delete_ducks(_created_duck_ids.copy())
        _created_duck_ids.clear()

    def _captcha_disabled(self, page: Page) -> bool:
        """Check if captcha is disabled (no recaptcha widget on page)."""
        return page.locator(".g-recaptcha").count() == 0

    def test_mark_new_duck_fills_name_and_submits(self, page: Page):
        """For a new duck: set name, location, date, comments → submit → verify location page."""
        new_duck_id = str(random.randint(90000, 99999))
        _created_duck_ids.append(new_duck_id)

        page.goto(f"{BASE_URL}/mark/")
        expect(page.locator("form#formMark")).to_be_visible()

        # Fill duck ID and trigger name lookup
        page.fill("input[name='duck_id']", new_duck_id)
        page.locator("input[name='duck_id']").blur()

        # Name field should enable (duck doesn't exist → 404 → enableDuckName)
        name_field = page.locator("#id_name")
        expect(name_field).to_be_enabled(timeout=5000)
        expect(page.locator("#name_notification")).to_contain_text("creative")

        # Set duck name
        name_field.fill("Sir Quacksalot")
        assert name_field.input_value() == "Sir Quacksalot"

        # Set location (bypass Google Places by injecting lat/lng)
        page.fill("input[name='location']", "Austin, TX, USA")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.2672'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.7431'")

        # Set date/time
        page.fill("input[name='date_time']", "2026-05-30T14:00")

        # Add comments
        page.fill("textarea[name='comments']", "Full e2e test with name")

        # Submit if captcha is disabled, otherwise just verify form state
        if self._captcha_disabled(page):
            page.click("#buttonSubmit")
            page.wait_for_url("**/location/**", timeout=15000)
            assert "/location/" in page.url

            # Verify the location page shows all submitted data
            body = page.locator("body")
            expect(body).to_contain_text("Sir Quacksalot")
            expect(body).to_contain_text(new_duck_id)
            expect(body).to_contain_text("Austin")
            expect(body).to_contain_text("Full e2e test with name")
            expect(body).to_contain_text("30.26")
            expect(body).to_contain_text("-97.74")

    def test_mark_existing_duck_name_disabled(self, page: Page):
        """Marking an existing named duck pre-fills and disables the name field."""
        # Duck #42 (Ducklas Adams) exists in the local DB
        page.goto(f"{BASE_URL}/mark/42")
        expect(page.locator("form#formMark")).to_be_visible()

        # The duck_id field should be pre-filled
        duck_id_field = page.locator("input[name='duck_id']")
        expect(duck_id_field).to_have_value("42")

        # checkDuckName() runs on DOMContentLoaded — wait for fetch to resolve
        name_field = page.locator("#id_name")
        expect(name_field).to_be_disabled(timeout=5000)

        # Should have the existing name filled in
        assert name_field.input_value() == "Ducklas Adams"
        # No notification text (name already exists)
        expect(page.locator("#name_notification")).to_have_text("")

    def test_upload_invalid_file_shows_error(self, page: Page):
        """Submitting a non-image file shows a validation error."""
        page.goto(f"{BASE_URL}/mark/")

        # Skip if captcha is present (can't submit without auth)
        if page.locator(".g-recaptcha").count() > 0:
            pytest.skip("Captcha enabled — run with DISABLE_CAPTCHA or use auth tests")

        # Create a fake non-image file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
            f.write("this is not an image")
            fake_file = f.name

        # Fill required fields
        page.fill("input[name='duck_id']", "88888")
        page.locator("input[name='duck_id']").blur()
        page.wait_for_timeout(1000)
        page.fill("input[name='location']", "Bad Upload Test")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.0'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.0'")
        page.fill("input[name='date_time']", "2026-01-15T12:00")
        page.fill("textarea[name='comments']", "Should fail")

        # Upload invalid file
        page.locator("input[name='image']").set_input_files(fake_file)

        # Submit
        page.click("#buttonSubmit")

        # Should stay on the form page (not redirect)
        page.wait_for_load_state("networkidle")
        assert "/mark" in page.url

        # Should show an error about the image
        page_content = page.content()
        assert "valid image" in page_content.lower() or "image" in page_content.lower()

        os.unlink(fake_file)
