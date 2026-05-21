# Copilot Instructions for Duckiehunt

## Architecture

Duckiehunt is a Django web application for tracking rubber duck sightings on a map. It runs in Docker on an Azure VM with Traefik as reverse proxy, backed by SQLite.

- **Django app** lives in `django/` — the project is `duckiehunt`, the main app is `duck`
- **Settings** are split by environment: `django/duckiehunt/settings/{local,staging,production,development}.py`
- **Views** are function-based (not class-based) in `django/duck/views.py`
- **APIs** return raw `JsonResponse` (no DRF) in `django/duck/apis.py`
- **Business logic** (photo upload, distance calc, email) lives in `django/duck/marker.py`
- **Auth** uses `social-auth-app-django` for Google and Facebook OAuth2
- **Helm charts** in `charts/duckiehunt/` for Kubernetes deployments
- **Docker Compose** configs in `docker-compose/` — use `mac.yaml` for local dev

## Environment

Always activate the virtual environment before running any Python commands:

```bash
source venv/bin/activate
```

## Build & Run

```shell
# Setup
source venv/bin/activate
pip install -r ./django/requirements.txt
python manage.py migrate

# Run locally
# Run dev server (auto-logs in as first superuser)
python manage.py runserver 0.0.0.0:8042
# Access at http://localhost:8042

# Django shell inside the container
docker exec -it duckiehunt-local python manage.py shell

# Run database migrations
docker exec -it duckiehunt-local python manage.py migrate
```

## Testing

Tests use **Playwright** (Python) and live in `tests/`. They run against a local instance.

```shell
# Install test dependencies
pip install playwright pytest-playwright setuptools flickr-api
playwright install

# Run all basic tests
pytest tests/test_basic.py

# Run a single test
pytest tests/test_basic.py::test_homepage_has_Duckiehunt_in_title_and_mark_link

# Run with visible browser
pytest --headed tests/test_basic.py

# Authenticated tests (requires auth.json)
pytest tests/test_mark_duck.py
```

## Key Conventions

- Models use explicit `db_table` names in Meta (e.g., `duck`, `duck_location`) — do not rely on Django's auto-naming
- URL routing: views at human-readable paths (`/duck/5`), APIs under `/api/` prefix
- Photo storage uses Flickr API via `flickr_api` library (migration to Imgur planned)
- The container image is published to `ghcr.io/lastcoolnameleft/duckiehunt`
- CI builds and deploys on push to `master` branch
- Python dependencies managed with `pip-compile` from `requirements.in` → `requirements.txt` in `django/`
