# Scrooge — History

## Learnings

- Project: duckiehunt — Django app for tracking rubber duck sightings on a map
- Stack: Python, Django, SQLite, Docker, Traefik reverse proxy, Helm/K8s
- User: Tommy Falgout
- Django app in `django/`, project is `duckiehunt`, main app is `duck`
- Function-based views, raw JsonResponse APIs (no DRF)
- Auth via social-auth-app-django (Google/Facebook OAuth2)
- Tests use Playwright (Python) in `tests/`
