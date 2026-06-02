#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source venv/bin/activate
cd django
python manage.py migrate --run-syncdb

# Run both the web server and the task queue worker, interleaving logs
python manage.py qcluster &
WORKER_PID=$!

# Ensure worker is stopped when the script exits
trap "kill $WORKER_PID 2>/dev/null" EXIT

python manage.py runserver 0.0.0.0:8042
