#!/bin/bash

# Azure deployment script for Django
echo "Starting Azure deployment..."

# Install Python dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Deployment completed successfully!"
