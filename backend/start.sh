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

echo "Starting Daphne on 0.0.0.0:${PORT:-8000}..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} posture_project.asgi:application
