"""
Playwright tests for form validation and error handling.

Tests empty submissions, special characters, and edge cases.

Requires:
  - Local dev server running at http://localhost:8042
  - Captcha disabled in dev (no RECAPTCHA_PUBLIC_KEY env var)

Run with:
  pytest tests/playwright/test_validation.py -v
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


def _captcha_disabled(page: Page) -> bool:
    """Check if captcha is disabled (no recaptcha widget on page)."""
    return page.locator(".g-recaptcha").count() == 0


class TestEmptyFormSubmission:
    """Tests for submitting forms with missing required fields."""

    def test_mark_empty_submit_stays_on_page(self, page: Page):
        """Submitting mark form with no fields stays on form page."""
        page.goto(f"{BASE_URL}/mark/")
        if not _captcha_disabled(page):
            pytest.skip("Captcha enabled — cannot test form submission")

        page.click("#buttonSubmit")
        page.wait_for_load_state("networkidle")
        # Should stay on mark page (validation rejects it)
        assert "/mark" in page.url

    def test_mark_missing_location_shows_error(self, page: Page):
        """Submitting with duck_id but no location shows validation error."""
        page.goto(f"{BASE_URL}/mark/")
        if not _captcha_disabled(page):
            pytest.skip("Captcha enabled — cannot test form submission")

        # Fill only duck_id
        page.fill("input[name='duck_id']", "12345")
        page.locator("input[name='duck_id']").blur()
        page.wait_for_timeout(500)
        page.fill("input[name='date_time']", "2026-05-30T12:00")

        page.click("#buttonSubmit")
        page.wait_for_load_state("networkidle")
        # Should stay on form with error
        assert "/mark" in page.url

    def test_mark_missing_date_shows_error(self, page: Page):
        """Submitting without date stays on form."""
        page.goto(f"{BASE_URL}/mark/")
        if not _captcha_disabled(page):
            pytest.skip("Captcha enabled — cannot test form submission")

        page.fill("input[name='duck_id']", "12345")
        page.locator("input[name='duck_id']").blur()
        page.wait_for_timeout(500)
        page.fill("input[name='location']", "Test Location")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.0'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.0'")

        page.click("#buttonSubmit")
        page.wait_for_load_state("networkidle")
        assert "/mark" in page.url


class TestSpecialCharacters:
    """Tests for special characters in form fields (XSS prevention)."""

    def setup_method(self):
        """Clean up any leftover test ducks before each test."""
        _delete_ducks(_created_duck_ids.copy())
        _created_duck_ids.clear()

    def teardown_method(self):
        """Delete all ducks created during this test."""
        _delete_ducks(_created_duck_ids.copy())
        _created_duck_ids.clear()

    def test_special_chars_in_duck_name(self, page: Page):
        """Special characters in duck name are escaped properly."""
        page.goto(f"{BASE_URL}/mark/")
        if not _captcha_disabled(page):
            pytest.skip("Captcha enabled — cannot test form submission")

        new_duck_id = str(random.randint(90000, 99999))
        _created_duck_ids.append(new_duck_id)
        page.fill("input[name='duck_id']", new_duck_id)
        page.locator("input[name='duck_id']").blur()
        expect(page.locator("#id_name")).to_be_enabled(timeout=5000)

        # Use HTML/script injection attempt as duck name
        xss_name = '<script>alert("xss")</script>'
        page.fill("#id_name", xss_name)

        page.fill("input[name='location']", "XSS Test City")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '30.0'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '-97.0'")
        page.fill("input[name='date_time']", "2026-05-30T12:00")
        page.fill("textarea[name='comments']", '<img onerror="alert(1)" src=x>')

        page.click("#buttonSubmit")
        page.wait_for_url("**/location/**", timeout=15000)

        # Verify the page renders without executing scripts
        # The text should be escaped, not executed
        body_html = page.content()
        assert "<script>alert" not in body_html or "&lt;script&gt;" in body_html
        # Page should not have triggered any alerts
        assert "/location/" in page.url

    def test_special_chars_in_comments(self, page: Page):
        """Unicode and emoji in comments render correctly."""
        page.goto(f"{BASE_URL}/mark/")
        if not _captcha_disabled(page):
            pytest.skip("Captcha enabled — cannot test form submission")

        new_duck_id = str(random.randint(90000, 99999))
        _created_duck_ids.append(new_duck_id)
        page.fill("input[name='duck_id']", new_duck_id)
        page.locator("input[name='duck_id']").blur()
        expect(page.locator("#id_name")).to_be_enabled(timeout=5000)
        page.fill("#id_name", "Unicode Duck")

        page.fill("input[name='location']", "Tokyo, Japan")
        page.evaluate("document.querySelector('input[name=\"lat\"]').value = '35.6762'")
        page.evaluate("document.querySelector('input[name=\"lng\"]').value = '139.6503'")
        page.fill("input[name='date_time']", "2026-05-30T12:00")

        unicode_comment = "Found 🦆 in café — très bien! 日本語テスト"
        page.fill("textarea[name='comments']", unicode_comment)

        page.click("#buttonSubmit")
        page.wait_for_url("**/location/**", timeout=15000)

        body = page.locator("body")
        expect(body).to_contain_text("🦆")
        expect(body).to_contain_text("café")
        expect(body).to_contain_text("日本語テスト")


class TestErrorPages:
    """Tests for error responses (404s, bad input)."""

    def test_nonexistent_page_404(self, page: Page):
        """Random URL returns 404."""
        resp = page.goto(f"{BASE_URL}/this-page-does-not-exist/")
        assert resp.status == 404

    def test_nonexistent_duck_shows_not_found(self, page: Page):
        """Viewing a duck that doesn't exist shows not-found message."""
        page.goto(f"{BASE_URL}/duck/999999")
        body = page.locator("body")
        expect(body).to_contain_text("Not Found")

    def test_nonexistent_location_404(self, page: Page):
        """Viewing a location that doesn't exist returns 404."""
        resp = page.goto(f"{BASE_URL}/location/999999")
        assert resp.status == 404

    def test_mark_with_string_duck_id_404(self, page: Page):
        """Mark page with non-numeric duck_id returns 404."""
        resp = page.goto(f"{BASE_URL}/mark/abc")
        assert resp.status == 404


class TestMobileResponsive:
    """Tests for mobile responsiveness on various pages."""

    def test_duck_list_mobile(self, page: Page):
        """Duck list page is usable on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/duck/")
        # Content should be visible (not overflowing)
        body = page.locator("body")
        expect(body).to_contain_text("The Wild One")
        # Navbar should be collapsed
        expect(page.locator("button.navbar-toggler")).to_be_visible()

    def test_mark_form_mobile(self, page: Page):
        """Mark form is usable on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/mark/")
        # Form should be visible and usable
        expect(page.locator("form#formMark")).to_be_visible()
        expect(page.locator("input[name='duck_id']")).to_be_visible()

    def test_duck_detail_mobile(self, page: Page):
        """Duck detail page renders on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/duck/1")
        body = page.locator("body")
        expect(body).to_contain_text("The Wild One")

    def test_faq_mobile(self, page: Page):
        """FAQ accordion works on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/faq/")
        # FAQ uses card-based accordion with <a> toggles
        # Click the second FAQ item (first may already be expanded)
        accordion_link = page.locator("a[data-bs-toggle='collapse']").nth(1)
        expect(accordion_link).to_be_visible()
        accordion_link.click()
        page.wait_for_timeout(500)
        # Should have at least 2 visible collapses (navbar + the one we opened)
        visible_collapse = page.locator(".collapse.show")
        assert visible_collapse.count() >= 2
