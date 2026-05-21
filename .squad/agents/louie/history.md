# Louie — History

## Learnings

- Project: duckiehunt — Django app for tracking rubber duck sightings on a map
- Stack: Playwright (Python), pytest, pytest-playwright
- User: Tommy Falgout
- Tests in `tests/` using Playwright Python
- Run all: `pytest tests/test_basic.py`
- Single test: `pytest tests/test_basic.py::test_homepage_has_Duckiehunt_in_title_and_mark_link`
- Headed mode: `pytest --headed tests/test_basic.py`
- Auth tests (test_mark_duck.py) require auth.json
- Install deps: `pip install playwright pytest-playwright setuptools flickr-api && playwright install`

## Recent Work (2026-05-21T16:40)

- Created `tests/staging/test_smoke.py` with 8 smoke tests
  - Tests: homepage load, health check, login page load, mark page load, OAuth flow surfaces
  - Uses `requests` and `pytest` (CI-friendly, no browser)
  - Configurable via `DUCKIEHUNT_STAGING_URL` env var
  - Polls for readiness before test run
- Created `tests/production/test_smoke.py` with 5 critical path tests
  - Minimal subset: homepage, health, mark page surface
  - Same polling and env var pattern as staging
- Both suites designed for Dewey's CI workflows
