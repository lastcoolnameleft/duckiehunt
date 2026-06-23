"""Pytest configuration for staging tests."""
import os

import pytest

# Load .env from repo root for local dev (optional in CI where secrets are injected)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def pytest_collection_modifyitems(config, items):
    """Skip Playwright tests if credentials are not available."""
    if not os.environ.get("TEST_USERNAME"):
        skip_marker = pytest.mark.skip(reason="TEST_USERNAME not set")
        for item in items:
            if "authenticated_page" in getattr(item, "fixturenames", []):
                item.add_marker(skip_marker)
