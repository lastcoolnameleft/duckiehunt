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
