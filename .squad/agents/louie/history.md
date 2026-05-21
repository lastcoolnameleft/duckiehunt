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
