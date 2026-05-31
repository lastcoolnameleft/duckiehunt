"""
Playwright tests for JSON API endpoints.

Requires:
  - Local dev server running at http://localhost:8042
  - At least one duck with locations in the database

Run with:
  pytest tests/playwright/test_api.py -v
"""
import json
import os

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


class TestHealthAPI:
    """Tests for /api/health endpoint."""

    def test_health_returns_200(self, page: Page):
        """Health endpoint returns 200 OK."""
        resp = page.goto(f"{BASE_URL}/api/health")
        assert resp.status == 200

    def test_health_returns_json(self, page: Page):
        """Health endpoint returns valid JSON."""
        page.goto(f"{BASE_URL}/api/health")
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert "status" in data or isinstance(data, dict)


class TestVersionAPI:
    """Tests for /api/version endpoint."""

    def test_version_returns_200(self, page: Page):
        """Version endpoint returns 200 OK."""
        resp = page.goto(f"{BASE_URL}/api/version")
        assert resp.status == 200

    def test_version_returns_json(self, page: Page):
        """Version endpoint returns valid JSON."""
        page.goto(f"{BASE_URL}/api/version")
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert isinstance(data, dict)


class TestDuckAPI:
    """Tests for /api/duck/<id> endpoint."""

    def test_duck_detail_returns_json(self, page: Page):
        """Duck API returns JSON for existing duck."""
        resp = page.goto(f"{BASE_URL}/api/duck/1")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert "name" in data or "duck_id" in data

    def test_duck_detail_404_nonexistent(self, page: Page):
        """Duck API returns 404 for nonexistent duck."""
        resp = page.goto(f"{BASE_URL}/api/duck/999999")
        assert resp.status == 404


class TestDucksAllAPI:
    """Tests for /api/ducks endpoint."""

    def test_ducks_all_returns_list(self, page: Page):
        """Ducks list API returns a JSON array."""
        resp = page.goto(f"{BASE_URL}/api/ducks")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_ducks_all_contains_duck_fields(self, page: Page):
        """Each duck in the list has expected fields."""
        page.goto(f"{BASE_URL}/api/ducks")
        body = page.locator("body").inner_text()
        data = json.loads(body)
        first = data[0]
        # Should have identifying fields
        assert "duck_id" in first or "pk" in first or "name" in first


class TestLocationsAPI:
    """Tests for /api/locations endpoint."""

    def test_locations_all_returns_list(self, page: Page):
        """Locations API returns a JSON array."""
        resp = page.goto(f"{BASE_URL}/api/locations")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert isinstance(data, list)
        assert len(data) > 0


class TestDuckLocationsAPI:
    """Tests for /api/duck/<id>/locations endpoint."""

    def test_duck_locations_returns_list(self, page: Page):
        """Duck locations API returns locations for a specific duck."""
        resp = page.goto(f"{BASE_URL}/api/duck/1/locations")
        assert resp.status == 200
        body = page.locator("body").inner_text()
        data = json.loads(body)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_duck_locations_empty_for_nonexistent(self, page: Page):
        """Duck locations API returns empty or 404 for nonexistent duck."""
        resp = page.goto(f"{BASE_URL}/api/duck/999999/locations")
        # Either empty list or 404 is acceptable
        assert resp.status in (200, 404)


class TestLocationAPI:
    """Tests for /api/location/<id> endpoint."""

    def test_location_detail_returns_json(self, page: Page):
        """Location API returns JSON for existing location."""
        # First get a valid location ID from the locations list
        page.goto(f"{BASE_URL}/api/duck/1/locations")
        body = page.locator("body").inner_text()
        locations = json.loads(body)
        if not locations:
            pytest.skip("No locations in database")

        loc = locations[0]
        loc_id = loc.get("pk") or loc.get("duck_location_id") or loc.get("id")
        if not loc_id:
            pytest.skip("Cannot determine location ID from API response")

        resp = page.goto(f"{BASE_URL}/api/location/{loc_id}")
        assert resp.status == 200
