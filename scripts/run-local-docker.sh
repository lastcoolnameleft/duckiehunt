#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE=".env.local-docker"
COMPOSE_OVERRIDE="$SCRIPT_DIR/docker-compose.local-docker.override.yml"

cd "$PROJECT_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found in $PROJECT_DIR"
    exit 1
fi

if [[ ! -f "$COMPOSE_OVERRIDE" ]]; then
    echo "Error: $COMPOSE_OVERRIDE not found"
    exit 1
fi

echo "==> Running Docker Build..."
docker build -t duckiehunt:local .

echo "==> Starting duckiehunt locally with $ENV_FILE..."
docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f "$COMPOSE_OVERRIDE" up --build --force-recreate
