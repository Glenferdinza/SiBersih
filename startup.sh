#!/bin/sh

# Azure startup script
# This script is executed when the container starts

echo "Starting Gunicorn..."

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn config.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --threads=2 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info
