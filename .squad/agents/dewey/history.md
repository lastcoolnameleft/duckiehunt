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
