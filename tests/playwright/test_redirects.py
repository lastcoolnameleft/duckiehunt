"""
Playwright tests for legacy URL redirects and navigation.

Verifies that old /view/duck/ and /view/location/ URLs redirect
to their modern equivalents.

Requires:
  - Local dev server running at http://localhost:8042
  - At least one duck and location in the database

Run with:
  pytest tests/playwright/test_redirects.py -v
"""
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


class TestLegacyRedirects:
    """Tests for /view/duck/ and /view/location/ legacy URLs."""

    def test_legacy_duck_url_resolves(self, page: Page):
        """/view/duck/<id> serves or redirects to duck detail."""
        resp = page.goto(f"{BASE_URL}/view/duck/1")
        # Should either redirect to /duck/1 or serve the same content
        body = page.locator("body")
        expect(body).to_contain_text("The Wild One")

    def test_legacy_location_url_resolves(self, page: Page):
        """/view/location/<id> serves or redirects to location detail."""
        resp = page.goto(f"{BASE_URL}/view/location/592")
        # Should serve location content
        body = page.locator("body")
        expect(body).to_contain_text("Tommy's Duckie")


class TestNavigationLinks:
    """Tests for internal navigation between pages."""

    def test_homepage_to_duck_list(self, page: Page):
        """Can navigate from homepage to duck list via nav."""
        page.goto(BASE_URL)
        page.locator("a.nav-link", has_text="View a duck").click()
        page.wait_for_load_state("networkidle")
        assert "/duck" in page.url

    def test_duck_list_to_duck_detail(self, page: Page):
        """Can click a duck in the list to view its detail page."""
        page.goto(f"{BASE_URL}/duck/")
        # Click the first duck link
        duck_link = page.locator("a[href*='/duck/']").first
        duck_link.click()
        page.wait_for_load_state("networkidle")
        assert "/duck/" in page.url

    def test_duck_detail_to_location(self, page: Page):
        """Can click a location on duck detail to view location page."""
        page.goto(f"{BASE_URL}/duck/1")
        loc_link = page.locator("a[href*='/location/']").first
        if loc_link.count() == 0:
            pytest.skip("No location links on duck detail page")
        loc_link.click()
        page.wait_for_load_state("networkidle")
        assert "/location/" in page.url

    def test_footer_faq_link(self, page: Page):
        """Footer FAQ link navigates to FAQ page."""
        page.goto(BASE_URL)
        page.locator("footer a[href*='faq']").click()
        assert "/faq" in page.url

    def test_found_a_duck_link(self, page: Page):
        """'Found a Duck?' CTA navigates to mark page."""
        page.goto(BASE_URL)
        page.locator("a:has-text('Found a Duck')").click()
        page.wait_for_url(f"{BASE_URL}/mark/")
        assert "/mark" in page.url
