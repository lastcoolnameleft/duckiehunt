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

### Django unit tests

```shell
source venv/bin/activate
cd django && python manage.py test duck.tests --verbosity=2
```

### Playwright tests (local, requires running dev server)

All local Playwright browser tests live in `tests/playwright/`.

```shell
# Install test dependencies
pip install playwright pytest-playwright setuptools flickr-api
playwright install

# Run all local Playwright tests
pytest tests/playwright/ -v

# Run with visible browser
pytest tests/playwright/ -v --headed

# Run a specific test
pytest tests/playwright/test_basic.py -v

# Authenticated tests (requires auth.json at repo root)
pytest tests/playwright/test_mark_duck.py --headed
pytest tests/playwright/test_photo_upload.py -v --headed
```

### Staging/Production tests (CI)

These run automatically in GitHub Actions against deployed environments:
- `tests/staging/` — runs after deploy to staging
- `tests/production/` — runs against production

## Git & GitHub Workflow

- Use `Fixes #N` in commit messages to auto-close GitHub issues when pushed to master
- Do NOT manually close issues with `gh issue close` — let GitHub handle it on push
- CI builds and deploys on push to `master` branch
- Always separate `git add` and `git commit` into two steps — stage first, wait for user approval, then commit
- Never combine `git add` and `git commit` into a single command

## Key Conventions

- Models use explicit `db_table` names in Meta (e.g., `duck`, `duck_location`) — do not rely on Django's auto-naming
- URL routing: views at human-readable paths (`/duck/5`), APIs under `/api/` prefix
- Photo storage uses Flickr API via `flickr_api` library (migration to Imgur planned)
- The container image is published to `ghcr.io/lastcoolnameleft/duckiehunt`
- Python dependencies managed with `pip-compile` from `requirements.in` → `requirements.txt` in `django/`
- `marker.py:26` — `User.objects.get(id=1)` in `add_initial_duck_location` is intentional (owner's wedding venue/date as duck origin)
