#!/bin/sh
set -e

# Ensure appuser owns writable directories (handles root-owned volumes)
if [ "$(id -u)" = "0" ]; then
  chown -R appuser:appuser /app/data /app/uploads
  exec gosu appuser "$0" "$@"
fi

echo "Running migrations..."
python manage.py migrate --noinput

exec gunicorn duckiehunt.wsgi:application --bind 0.0.0.0:8000
