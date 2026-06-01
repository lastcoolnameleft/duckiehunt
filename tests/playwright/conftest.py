"""Pytest configuration for Playwright integration tests."""
import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "staging_safe: test can run against a remote staging environment (read-only, no DB access needed)"
    )
