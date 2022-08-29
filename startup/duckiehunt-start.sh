#!/bin/bash

echo "Starting mgmt"
docker compose --file /home/thfalgou/duckiehunt/docker-compose/management.yaml up -d
echo "Starting dev"
docker compose --file /home/thfalgou/duckiehunt/docker-compose/development.yaml up -d
echo "Starting stg"
docker compose --file /home/thfalgou/duckiehunt/docker-compose/staging.yaml up -d
echo "Starting prod"
docker compose --file /home/thfalgou/duckiehunt/docker-compose/production.yaml up -d