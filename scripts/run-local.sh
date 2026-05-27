#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source venv/bin/activate
cd django
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8042
