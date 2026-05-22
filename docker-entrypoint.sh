#!/bin/sh
set -e

mkdir -p /app/data /app/uploads

# Ensure appuser owns the data and uploads directories (handles root-owned volumes)
if [ "$(id -u)" = "0" ]; then
  chown -R appuser:appuser /app/data /app/uploads
  exec gosu appuser "$0" "$@"
fi

echo "Running migrations..."
python manage.py migrate --noinput

exec gunicorn duckiehunt.wsgi:application --bind 0.0.0.0:8000
