# Scrooge — History

## Learnings

- Project: duckiehunt — Django app for tracking rubber duck sightings on a map
- Stack: Python, Django, SQLite, Docker, Traefik reverse proxy, Helm/K8s
- User: Tommy Falgout
- Django app in `django/`, project is `duckiehunt`, main app is `duck`
- Function-based views, raw JsonResponse APIs (no DRF)
- Auth via social-auth-app-django (Google/Facebook OAuth2)
- Tests use Playwright (Python) in `tests/`
- 2026-05-21T15:31:09.000-05:00: Proposed Docker migration should converge on one env-driven `django/duckiehunt/settings.py`, one deploy `docker-compose.yml`, and staged image promotion (`latest` -> staging, `prod` -> production).
- 2026-05-21T15:31:09.000-05:00: Current deployment drift is concentrated in `docker-compose/{mac,staging,production,development}.yaml`, host-mounted `/data/duckiehunt-{env}/settings` volumes, and GitHub workflows in `.github/workflows/`.
- 2026-05-21T15:31:09.000-05:00: Duckiehunt-specific env surface must cover Flickr, Google/Facebook OAuth, SendGrid, reCAPTCHA, base URL/email settings, and the Google Maps keys now hardcoded in `django/duck/templates/duck/mark.html` and `django/duck/templates/duck/view/map.html`.
- 2026-05-21T15:31:09.000-05:00: Keep local-dev ergonomics, but fold them into the unified compose path via local env/profile support rather than preserving long-lived per-environment compose files.
