#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-true}" != "false" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
fi

# Create/update test user if credentials are provided
if [ -n "$TEST_USERNAME" ] && [ -n "$TEST_PASSWORD" ]; then
  echo "Ensuring test user exists..."
  python manage.py shell -c "
from django.contrib.auth.models import User
user, created = User.objects.get_or_create(username='$TEST_USERNAME', defaults={'is_active': True})
user.set_password('$TEST_PASSWORD')
user.is_active = True
user.save()
print(f'Test user {user.username} {\"created\" if created else \"updated\"}')
"
fi

# If a command was specified (e.g., for worker), use it; otherwise run gunicorn
if [ $# -gt 0 ]; then
  exec "$@"
else
  exec gunicorn duckiehunt.wsgi:application --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
fi
