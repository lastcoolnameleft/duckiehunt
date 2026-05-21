#!/bin/sh
set -e

mkdir -p /app/data /app/uploads

echo "Running migrations..."
python manage.py migrate --noinput

exec gunicorn duckiehunt.wsgi:application --bind 0.0.0.0:8000
