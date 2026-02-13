#!/bin/bash

echo "=== PostureScore backend starting ==="

echo "PORT=$PORT"

# Run migrations (retry once if DB isn't ready yet)
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "Migration failed, retrying in 5s..."
    sleep 5
    python manage.py migrate --noinput
}

# Create superuser from env vars (defaults: admin/admin)
export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
export DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin}"

echo "Ensuring superuser '${DJANGO_SUPERUSER_USERNAME}' exists..."
python manage.py createsuperuser --noinput 2>/dev/null || true
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
u = User.objects.get(username=os.environ['DJANGO_SUPERUSER_USERNAME'])
u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD'])
u.is_superuser = True
u.save()
print('Superuser password updated.')
"

# Seed exercises (idempotent — only creates missing exercises)
echo "Seeding exercises..."
python manage.py seed_exercises

echo "Starting Daphne on 0.0.0.0:${PORT:-8000}..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} posture_project.asgi:application
