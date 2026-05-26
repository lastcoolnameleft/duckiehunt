#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

# Create/update staging test user if credentials are provided
if [ -n "$STG_TEST_USERNAME" ] && [ -n "$STG_TEST_PASSWORD" ]; then
  echo "Ensuring staging test user exists..."
  python manage.py shell -c "
from django.contrib.auth.models import User
user, created = User.objects.get_or_create(username='$STG_TEST_USERNAME', defaults={'is_staff': True, 'is_active': True})
user.set_password('$STG_TEST_PASSWORD')
user.is_staff = True
user.is_active = True
user.save()
print(f'Test user {user.username} {\"created\" if created else \"updated\"}')
"
fi

exec gunicorn duckiehunt.wsgi:application --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
