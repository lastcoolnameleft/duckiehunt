"""Pytest configuration for staging tests."""
import os

import pytest
from dotenv import load_dotenv

# Load .env from repo root so tests pick up STG_* vars
load_dotenv()


def pytest_collection_modifyitems(config, items):
    """Skip Playwright tests if credentials are not available."""
    if not os.environ.get("STG_TEST_USERNAME"):
        skip_marker = pytest.mark.skip(reason="STG_TEST_USERNAME not set")
        for item in items:
            if "authenticated_page" in getattr(item, "fixturenames", []):
                item.add_marker(skip_marker)
