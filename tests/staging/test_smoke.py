"""
Staging smoke tests — run against a live deployed instance.
Run with: pytest tests/staging/ -v
"""
import os
import re

import pytest
import requests


def _extract_title(html):
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


@pytest.fixture(scope="session")
def base_url():
    url = os.environ.get("STG_BASE_URL", "http://localhost:8042")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def anon_session():
    return requests.Session()


class TestPublicEndpoints:
    def test_health_endpoint(self, base_url, anon_session):
        resp = anon_session.get(f"{base_url}/api/health", timeout=10)
        assert resp.status_code == 200

        data = resp.json()
        assert data["status"] == "ok"
        assert data["db"] is True
        assert "sha" in data

    def test_version_endpoint(self, base_url, anon_session):
        resp = anon_session.get(f"{base_url}/api/version", timeout=10)
        assert resp.status_code == 200

        data = resp.json()
        assert "git_sha" in data

    def test_home_page(self, base_url, anon_session):
        resp = anon_session.get(f"{base_url}/", timeout=10)
        assert resp.status_code == 200
        assert "Duckiehunt" in _extract_title(resp.text)

    def test_duck_list_page(self, base_url, anon_session):
        resp = anon_session.get(f"{base_url}/duck/", timeout=10)
        assert resp.status_code == 200
        assert "View a Duck" in resp.text

    @pytest.mark.parametrize(
        ("path", "expected_text"),
        [
            ("/faq/", "FAQ"),
            ("/privacy/", "PRIVACY POLICY"),
            ("/tos/", "TERMS OF USE"),
        ],
    )
    def test_public_info_pages(self, base_url, anon_session, path, expected_text):
        resp = anon_session.get(f"{base_url}{path}", timeout=10)
        assert resp.status_code == 200
        assert expected_text in resp.text

    def test_ducks_api(self, base_url, anon_session):
        resp = anon_session.get(f"{base_url}/api/ducks", timeout=10)
        assert resp.status_code == 200

        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert {"duck_id", "name", "total_distance"}.issubset(data[0])
