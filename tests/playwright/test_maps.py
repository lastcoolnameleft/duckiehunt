"""
Playwright test verifying Google Maps renders on mark and view pages.

Requires:
  - Local dev server running at http://localhost:8042
  - GOOGLE_MAPS_API_KEY configured in the server environment
  - A duck with locations in the database (duck_id=1 or similar)

Run with:
  pytest tests/test_maps.py -v --headed
"""
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.staging_safe


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


class TestMapsRender:
    """Verify Google Maps loads and renders on map pages."""

    def test_map_renders_on_homepage(self, page: Page):
        """Homepage map container is present and Google Maps initializes."""
        page.goto(BASE_URL)
        # Map container should exist
        map_el = page.locator("#map")
        expect(map_el).to_be_visible()

        # Wait for Google Maps to initialize (adds tiles)
        page.wait_for_function(
            "document.querySelector('#map .gm-style') !== null",
            timeout=10000,
        )

    def test_map_renders_on_mark_page(self, page: Page):
        """Mark page map container loads with Google Maps."""
        page.goto(f"{BASE_URL}/mark/")
        map_el = page.locator("#map")
        expect(map_el).to_be_visible()

        page.wait_for_function(
            "document.querySelector('#map .gm-style') !== null",
            timeout=10000,
        )

    def test_map_renders_on_duck_detail(self, page: Page):
        """Duck detail page map loads (requires at least one duck in DB)."""
        # Navigate to found page which should redirect or show a duck
        page.goto(f"{BASE_URL}/duck/1")

        # If duck exists, map should render
        if page.locator("#map").count() > 0:
            page.wait_for_function(
                "document.querySelector('#map .gm-style') !== null",
                timeout=10000,
            )
        else:
            pytest.skip("No duck with id=1 in database")
