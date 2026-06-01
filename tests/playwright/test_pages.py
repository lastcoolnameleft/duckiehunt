"""
Playwright tests for read-only pages: duck list, duck detail, found,
FAQ, issue, TOS, privacy.

Requires:
  - Local dev server running at http://localhost:8042
  - At least one duck in the database (duck_id=1)

Run with:
  pytest tests/playwright/test_pages.py -v
"""
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.staging_safe


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


class TestDuckListPage:
    """Tests for /duck/ — list of all ducks."""

    def test_duck_list_loads(self, page: Page):
        """Duck list page renders with a table or list of ducks."""
        page.goto(f"{BASE_URL}/duck/")
        # Should contain at least one duck link
        duck_links = page.locator("a[href*='/duck/']")
        assert duck_links.count() > 0

    def test_duck_list_shows_duck_names(self, page: Page):
        """Duck list includes known duck names from the database."""
        page.goto(f"{BASE_URL}/duck/")
        body = page.locator("body")
        # Duck #1 "The Wild One" should appear
        expect(body).to_contain_text("The Wild One")

    def test_duck_list_has_navigation(self, page: Page):
        """Duck list page has standard navbar."""
        page.goto(f"{BASE_URL}/duck/")
        expect(page.locator("nav.navbar")).to_be_visible()


class TestDuckDetailPage:
    """Tests for /duck/<id> — individual duck view."""

    def test_duck_detail_loads(self, page: Page):
        """Duck detail page loads for an existing duck."""
        page.goto(f"{BASE_URL}/duck/1")
        body = page.locator("body")
        expect(body).to_contain_text("The Wild One")

    def test_duck_detail_shows_locations(self, page: Page):
        """Duck detail page shows location history."""
        page.goto(f"{BASE_URL}/duck/1")
        # Should have location entries (duck #1 has 7 locations)
        location_links = page.locator("a[href*='/location/']")
        assert location_links.count() > 0

    def test_duck_detail_shows_map(self, page: Page):
        """Duck detail page renders a map with location markers."""
        page.goto(f"{BASE_URL}/duck/1")
        map_el = page.locator("#map")
        expect(map_el).to_be_visible()

    def test_duck_detail_shows_distance(self, page: Page):
        """Duck with multiple locations shows total distance traveled."""
        page.goto(f"{BASE_URL}/duck/1")
        body = page.locator("body")
        # Should show distance info (duck #1 has 7 locations)
        page_text = body.inner_text()
        assert "mile" in page_text.lower() or "km" in page_text.lower() or "distance" in page_text.lower()

    def test_duck_detail_not_found_message(self, page: Page):
        """Nonexistent duck shows 'not found' message."""
        page.goto(f"{BASE_URL}/duck/999999")
        body = page.locator("body")
        expect(body).to_contain_text("Not Found")


class TestFoundPage:
    """Tests for /found/<id> — 'I found this duck' congratulations page."""

    def test_found_page_shows_congratulations(self, page: Page):
        """Found page shows congratulations and duck info."""
        page.goto(f"{BASE_URL}/found/1")
        body = page.locator("body")
        expect(body).to_contain_text("Congratulations")
        expect(body).to_contain_text("The Wild One")

    def test_found_page_links_to_mark(self, page: Page):
        """Found page has link to update the duck's location."""
        page.goto(f"{BASE_URL}/found/1")
        mark_link = page.locator("a[href*='/mark']")
        assert mark_link.count() > 0


class TestStaticPages:
    """Tests for TOS, Privacy, and Issue pages."""

    def test_tos_page_loads(self, page: Page):
        """Terms of Service page renders."""
        page.goto(f"{BASE_URL}/tos/")
        body = page.locator("body")
        page_text = body.inner_text().lower()
        assert "terms" in page_text or "service" in page_text

    def test_privacy_page_loads(self, page: Page):
        """Privacy policy page renders."""
        page.goto(f"{BASE_URL}/privacy/")
        body = page.locator("body")
        page_text = body.inner_text().lower()
        assert "privacy" in page_text

    def test_issue_page_loads(self, page: Page):
        """Issue reporting page renders with accordion."""
        page.goto(f"{BASE_URL}/issue/")
        expect(page.locator("body")).to_contain_text("issue")

    def test_tos_has_navbar(self, page: Page):
        """Static pages include standard navigation."""
        page.goto(f"{BASE_URL}/tos/")
        expect(page.locator("nav.navbar")).to_be_visible()

    def test_privacy_has_navbar(self, page: Page):
        """Static pages include standard navigation."""
        page.goto(f"{BASE_URL}/privacy/")
        expect(page.locator("nav.navbar")).to_be_visible()
