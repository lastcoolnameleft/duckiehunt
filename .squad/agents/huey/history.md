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
