# Huey — History

## Learnings

- Project: duckiehunt — Django app for tracking rubber duck sightings on a map
- Stack: Python, Django, SQLite
- User: Tommy Falgout
- Django app in `django/`, project is `duckiehunt`, main app is `duck`
- Function-based views in `django/duck/views.py`
- APIs return raw JsonResponse in `django/duck/apis.py`
- Business logic (photo upload, distance calc, email) in `django/duck/marker.py`
- Models use explicit `db_table` names in Meta
- Python deps managed with pip-compile: requirements.in → requirements.txt in `django/`
- 2026-05-21T16:09:33.231-05:00: `duckiehunt.settings` is now the package entrypoint in `django/duckiehunt/settings/__init__.py`, with legacy per-environment modules preserved alongside it.

## Recent Work (2026-05-21T16:40)

- Added `/api/health` endpoint in `django/duck/apis.py` returning `{"status": "ok"}`
- Registered route in `django/duck/urls.py` as `path("api/health/", health, name="health")`
- Validated with `manage.py check` and Django shell test
- Provides readiness signal for CI deploy polling

## Recent Work (2026-05-21T22:36)

- Regenerated `django/requirements.txt` with `pip-compile --upgrade requirements.in` to clear Dependabot alerts
- Upgraded key packages including Django 6.0.5, urllib3 2.7.0, cryptography 48.0.0, requests 2.34.2, PyJWT 2.13.0, idna 3.16, social-auth-app-django 5.9.0, and sqlparse 0.5.5
- Installed the refreshed lockfile and validated with `DATABASE_PATH=db/duckiehunt.db python django/manage.py check`

## Recent Work (2026-05-21T22:39)

- Added `python-dotenv` to `django/requirements.in` and regenerated the pinned `django/requirements.txt` so unified settings can import `load_dotenv`
- Updated the Docker build to use `DJANGO_SETTINGS_MODULE=duckiehunt.settings` for both the image environment and the `collectstatic` build step
- Checked `docker-entrypoint.sh`; it does not set `DJANGO_SETTINGS_MODULE`, so no entrypoint change was needed
- Revalidated settings loading with `DATABASE_PATH=db/duckiehunt.db python django/manage.py check`
