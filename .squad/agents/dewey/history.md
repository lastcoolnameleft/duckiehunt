# Dewey — History

## Learnings

- Project: duckiehunt — Django app for tracking rubber duck sightings on a map
- Stack: Docker, Traefik, Helm/K8s, GitHub Actions
- User: Tommy Falgout
- Docker Compose configs in `docker-compose/`, use `mac.yaml` for local dev
- Helm charts in `charts/duckiehunt/`
- Container image published to `ghcr.io/lastcoolnameleft/duckiehunt`
- CI builds and deploys on push to `master` branch
- Runs on Azure VM with Traefik as reverse proxy
- 2026-05-21T16:09:33.231-05:00: The new deployment path uses a root `docker-compose.yml` plus env files, while the image keeps legacy `/code`, `/db`, and `/uploads` paths alive via symlinks so settings modules can keep working during migration.

## Recent Work (2026-05-21T16:40)

- Created `.github/workflows/staging-tests.yml` CI workflow
  - Runs after staging deployment, polls for readiness via `/api/health`
  - Executes smoke tests (Louie's test suite)
  - Creates GitHub issue on test failure with console output
- Created `.github/workflows/production-tests.yml` CI workflow
  - Runs production smoke tests with manual trigger option
  - Same issue creation and console logging on failure
- Both workflows integrated with Huey's health endpoint for deploy polling
